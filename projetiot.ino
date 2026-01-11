#include <WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include <Firebase_ESP_Client.h>
#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"

// Configuration WiFi
const char* ssid = "Galaxy de ahmed";
const char* password = "kkkkkkkk";

// Configuration MQTT
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;

// Configuration Firebase
#define FIREBASE_HOST "https://gestion-ee-default-rtdb.europe-west1.firebasedatabase.app"
#define API_KEY "AIzaSyCj8I0pNNMAlKltT3BcMHVpvX5DiRaCyuQ"
#define USER_EMAIL "ahmedbenaicha075@gmail.com"
#define USER_PASSWORD "green000"

// Pins RFID 1 (Inscription)
#define RST_PIN_1 22
#define SS_PIN_1 21

// Pins RFID 2 (Retrait/Retour)
#define RST_PIN_2 5
#define SS_PIN_2 4

// Pins LED et Buzzer
#define LED_VERT 25
#define LED_BLEU 26
#define LED_ROUGE 27
#define BUZZER 33

// Objets RFID
MFRC522 rfid1(SS_PIN_1, RST_PIN_1);
MFRC522 rfid2(SS_PIN_2, RST_PIN_2);

// Objects Firebase
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

WiFiClient espClient;
PubSubClient client(espClient);

// Variables d'état
bool mode_scan_inscription = false;
bool mode_scan_retrait = false;
bool mode_scan_retour = false;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n=== Démarrage système gestion stock ===");
  
  // Configuration des pins
  pinMode(LED_VERT, OUTPUT);
  pinMode(LED_BLEU, OUTPUT);
  pinMode(LED_ROUGE, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  
  // Test LED
  digitalWrite(LED_VERT, HIGH);
  delay(200);
  digitalWrite(LED_VERT, LOW);
  digitalWrite(LED_BLEU, HIGH);
  delay(200);
  digitalWrite(LED_BLEU, LOW);
  digitalWrite(LED_ROUGE, HIGH);
  delay(200);
  digitalWrite(LED_ROUGE, LOW);
  
  // Initialisation SPI
  Serial.println("Initialisation SPI...");
  SPI.begin();
  
  // Initialisation RFID #1
  Serial.println("Init RFID #1 (Inscription)...");
  rfid1.PCD_Init();
  delay(100);
  
  byte v1 = rfid1.PCD_ReadRegister(rfid1.VersionReg);
  Serial.print("RFID #1 Version: 0x");
  Serial.println(v1, HEX);
  
  if (v1 == 0x00 || v1 == 0xFF) {
    Serial.println("⚠️  ERREUR: RFID #1 non détecté!");
    Serial.println("Vérifiez: SDA→21, SCK→18, MOSI→23, MISO→19, RST→22, 3.3V");
    for(int i=0; i<5; i++) {
      digitalWrite(LED_ROUGE, HIGH);
      delay(200);
      digitalWrite(LED_ROUGE, LOW);
      delay(200);
    }
  } else {
    Serial.println("✓ RFID #1 OK");
  }
  
  // Initialisation RFID #2
  Serial.println("Init RFID #2 (Retrait/Retour)...");
  rfid2.PCD_Init();
  delay(100);
  
  byte v2 = rfid2.PCD_ReadRegister(rfid2.VersionReg);
  Serial.print("RFID #2 Version: 0x");
  Serial.println(v2, HEX);
  
  if (v2 == 0x00 || v2 == 0xFF) {
    Serial.println("⚠️  ERREUR: RFID #2 non détecté!");
    Serial.println("Vérifiez: SDA→4, SCK→18, MOSI→23, MISO→19, RST→5, 3.3V");
  } else {
    Serial.println("✓ RFID #2 OK");
  }
  
  // Connexion WiFi
  setup_wifi();
  
  // Configuration Firebase
  config.host = FIREBASE_HOST;
  config.api_key = API_KEY;
  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;
  config.token_status_callback = tokenStatusCallback;
  
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
  
  Serial.println("Connexion Firebase...");
  while (!Firebase.ready()) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("\n✓ Firebase connecté");
  
  // Configuration MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  
  Serial.println("\n=== Système prêt ===");
  Serial.println("En attente de commandes depuis Streamlit...");
  
  activerBuzzer();
}

void setup_wifi() {
  Serial.print("Connexion WiFi...");
  WiFi.begin(ssid, password);
  
  int tentatives = 0;
  while (WiFi.status() != WL_CONNECTED && tentatives < 20) {
    delay(500);
    Serial.print(".");
    tentatives++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi connecté");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n✗ Échec WiFi");
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  Serial.print("Message MQTT [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(message);
  
  // Commandes depuis Streamlit
  if (String(topic) == "stock/cmd/scan_inscription") {
    if (message == "START") {
      mode_scan_inscription = true;
      mode_scan_retrait = false;
      mode_scan_retour = false;
      Serial.println(">>> MODE INSCRIPTION ACTIVÉ <<<");
      digitalWrite(LED_BLEU, HIGH);
    }
  } 
  else if (String(topic) == "stock/cmd/scan_retrait") {
    if (message == "START") {
      mode_scan_retrait = true;
      mode_scan_inscription = false;
      mode_scan_retour = false;
      Serial.println(">>> MODE RETRAIT ACTIVÉ <<<");
      digitalWrite(LED_BLEU, HIGH);
    }
  }
  else if (String(topic) == "stock/cmd/scan_retour") {
    if (message == "START") {
      mode_scan_retour = true;
      mode_scan_inscription = false;
      mode_scan_retrait = false;
      Serial.println(">>> MODE RETOUR ACTIVÉ <<<");
      digitalWrite(LED_BLEU, HIGH);
    }
  }
  else if (String(topic) == "stock/led/vert") {
    digitalWrite(LED_VERT, message == "ON" ? HIGH : LOW);
  } 
  else if (String(topic) == "stock/led/bleu") {
    digitalWrite(LED_BLEU, message == "ON" ? HIGH : LOW);
  } 
  else if (String(topic) == "stock/led/rouge") {
    digitalWrite(LED_ROUGE, message == "ON" ? HIGH : LOW);
  } 
  else if (String(topic) == "stock/buzzer") {
    if (message == "BEEP") {
      activerBuzzer();
    }
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connexion MQTT...");
    String clientId = "ESP32-" + String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("✓");
      client.subscribe("stock/cmd/scan_inscription");
      client.subscribe("stock/cmd/scan_retrait");
      client.subscribe("stock/cmd/scan_retour");
      client.subscribe("stock/led/vert");
      client.subscribe("stock/led/bleu");
      client.subscribe("stock/led/rouge");
      client.subscribe("stock/buzzer");
    } else {
      Serial.print("✗ rc=");
      Serial.println(client.state());
      delay(5000);
    }
  }
}

void activerBuzzer() {
  digitalWrite(BUZZER, HIGH);
  delay(100);
  digitalWrite(BUZZER, LOW);
  delay(50);
  digitalWrite(BUZZER, HIGH);
  delay(100);
  digitalWrite(BUZZER, LOW);
}

String lireRFID(MFRC522 &rfid) {
  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();
  return uid;
}

void enregistrerUIDFirebase(String uid, String type) {
  if (Firebase.ready()) {
    String path = "/tags_scanned/" + uid;
    
    FirebaseJson json;
    json.set("uid", uid);
    json.set("type", type);
    json.set("timestamp", String(millis()));
    json.set("date", String(time(nullptr)));
    
    if (Firebase.RTDB.setJSON(&fbdo, path.c_str(), &json)) {
      Serial.println("✓ Firebase: UID enregistré");
    } else {
      Serial.println("✗ Firebase erreur: " + fbdo.errorReason());
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  // MODE INSCRIPTION (RFID 1)
  if (mode_scan_inscription) {
    rfid1.PCD_Init();
    delay(10);
    
    if (rfid1.PICC_IsNewCardPresent() && rfid1.PICC_ReadCardSerial()) {
      String uid = lireRFID(rfid1);
      
      Serial.println("\n✓ Badge scanné (INSCRIPTION)");
      Serial.print("UID: ");
      Serial.println(uid);
      
      // Enregistrer dans Firebase
      enregistrerUIDFirebase(uid, "inscription");
      
      // Publier sur MQTT
      String message = "{\"uid\":\"" + uid + "\"}";
      client.publish("stock/rfid/inscription", message.c_str());
      
      // Feedback
      digitalWrite(LED_BLEU, LOW);
      digitalWrite(LED_VERT, HIGH);
      activerBuzzer();
      delay(1500);
      digitalWrite(LED_VERT, LOW);
      
      mode_scan_inscription = false;
      
      rfid1.PICC_HaltA();
      rfid1.PCD_StopCrypto1();
    }
  }
  
  // MODE RETRAIT (RFID 2)
  if (mode_scan_retrait) {
    rfid2.PCD_Init();
    delay(10);
    
    if (rfid2.PICC_IsNewCardPresent() && rfid2.PICC_ReadCardSerial()) {
      String uid = lireRFID(rfid2);
      
      Serial.println("\n✓ Badge scanné (RETRAIT)");
      Serial.print("UID: ");
      Serial.println(uid);
      
      // Enregistrer dans Firebase
      enregistrerUIDFirebase(uid, "retrait");
      
      // Publier sur MQTT
      String message = "{\"uid\":\"" + uid + "\"}";
      client.publish("stock/rfid/retrait", message.c_str());
      
      // Feedback - LED verte pour scan ouvrier
      digitalWrite(LED_BLEU, LOW);
      digitalWrite(LED_VERT, HIGH);
      activerBuzzer();
      delay(1500);
      digitalWrite(LED_VERT, LOW);
      
      // LED bleue en attente de validation magasinier
      digitalWrite(LED_BLEU, HIGH);
      
      mode_scan_retrait = false;
      
      rfid2.PICC_HaltA();
      rfid2.PCD_StopCrypto1();
    }
  }
  
  // MODE RETOUR (RFID 2)
  if (mode_scan_retour) {
    rfid2.PCD_Init();
    delay(10);
    
    if (rfid2.PICC_IsNewCardPresent() && rfid2.PICC_ReadCardSerial()) {
      String uid = lireRFID(rfid2);
      
      Serial.println("\n✓ Badge scanné (RETOUR)");
      Serial.print("UID: ");
      Serial.println(uid);
      
      // Enregistrer dans Firebase
      enregistrerUIDFirebase(uid, "retour");
      
      // Publier sur MQTT
      String message = "{\"uid\":\"" + uid + "\"}";
      client.publish("stock/rfid/retour", message.c_str());
      
      // Feedback - LED rouge pour retour
      digitalWrite(LED_BLEU, LOW);
      digitalWrite(LED_ROUGE, HIGH);
      activerBuzzer();
      delay(1500);
      digitalWrite(LED_ROUGE, LOW);
      
      mode_scan_retour = false;
      
      rfid2.PICC_HaltA();
      rfid2.PCD_StopCrypto1();
    }
  }
  
  delay(100);
}
