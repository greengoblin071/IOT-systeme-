"""
MQTT Handler Optimisé - Version 2.0
Gestion temps réel avec callbacks et monitoring latence
"""

import paho.mqtt.client as mqtt
import threading
import json
import time
from datetime import datetime

class OptimizedMQTTHandler:
    def __init__(self, broker="localhost", port=1883):
        """
        Initialise le handler MQTT optimisé
        
        Args:
            broker: "localhost" pour local (plus rapide) ou "broker.hivemq.com" pour distant
            port: Port MQTT (défaut: 1883)
        """
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Stockage UID
        self.uid_inscription = None
        self.uid_transaction = None
        
        # Statistiques
        self.last_message_time = {}
        self.message_count = 0
        self.connected = False
        self.latency_history = []
        
        # Callbacks optionnels pour mise à jour immédiate
        self.on_uid_inscription_callback = None
        self.on_uid_transaction_callback = None
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback de connexion"""
        if rc == 0:
            self.connected = True
            # Subscribe avec QoS 1 pour garantir la réception
            client.subscribe("stock/rfid/inscription", qos=1)
            client.subscribe("stock/rfid/transaction", qos=1)
            client.subscribe("stock/status/#", qos=0)
            
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{timestamp}] [MQTT] ✓ Connecté à {self.broker}:{self.port}")
        else:
            self.connected = False
            print(f"[MQTT] ✗ Échec connexion (code: {rc})")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback de déconnexion"""
        self.connected = False
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        if rc != 0:
            print(f"[{timestamp}] [MQTT] ✗ Déconnexion inattendue (code: {rc})")
            print("[MQTT] Reconnexion automatique en cours...")
    
    def on_message(self, client, userdata, msg):
        """Callback de réception de message (optimisé pour latence)"""
        receive_time = time.time() * 1000  # Timestamp en ms
        
        try:
            data = json.loads(msg.payload.decode())
            topic = msg.topic
            
            # Calcul de la latence réseau si timestamp ESP32 disponible
            latency_info = ""
            if "timestamp" in data:
                esp_timestamp = data["timestamp"]
                network_latency = receive_time - esp_timestamp
                self.latency_history.append(network_latency)
                
                # Garder seulement les 50 dernières mesures
                if len(self.latency_history) > 50:
                    self.latency_history.pop(0)
                
                latency_info = f" | Latence: {network_latency:.0f}ms"
            
            self.message_count += 1
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{timestamp}] [MQTT] ← {topic} | #{self.message_count}{latency_info}")
            
            # Traitement selon le topic
            if topic == "stock/rfid/inscription":
                self.uid_inscription = data.get("uid", "")
                self.last_message_time["inscription"] = receive_time
                
                # Callback immédiat si défini
                if self.on_uid_inscription_callback:
                    self.on_uid_inscription_callback(self.uid_inscription)
                    
            elif topic == "stock/rfid/transaction":
                self.uid_transaction = data.get("uid", "")
                self.last_message_time["transaction"] = receive_time
                
                # Callback immédiat si défini
                if self.on_uid_transaction_callback:
                    self.on_uid_transaction_callback(self.uid_transaction)
                    
        except json.JSONDecodeError as e:
            print(f"[MQTT] ❌ Erreur JSON: {e}")
        except Exception as e:
            print(f"[MQTT] ❌ Erreur: {e}")
    
    def start(self):
        """Démarre la connexion MQTT en arrière-plan avec reconnexion auto"""
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()
        time.sleep(1)  # Attendre l'établissement de la connexion
        
        if self.connected:
            print(f"[MQTT] ✓ Thread MQTT démarré et connecté")
        else:
            print(f"[MQTT] ⚠ Thread démarré mais connexion en cours...")
    
    def _loop(self):
        """Boucle de connexion avec reconnexion automatique"""
        while True:
            try:
                print(f"[MQTT] Tentative de connexion à {self.broker}:{self.port}...")
                self.client.connect(self.broker, self.port, 60)
                self.client.loop_forever()
            except ConnectionRefusedError:
                print(f"[MQTT] ❌ Connexion refusée par {self.broker}:{self.port}")
                print("[MQTT] Vérifiez que le broker MQTT est lancé")
                print("[MQTT] Nouvelle tentative dans 5s...")
                time.sleep(5)
            except Exception as e:
                print(f"[MQTT] ❌ Erreur: {e}")
                print("[MQTT] Nouvelle tentative dans 5s...")
                time.sleep(5)
    
    def publish(self, topic, message):
        """Publie un message avec mesure de latence"""
        if not self.connected:
            print("[MQTT] ⚠ Non connecté, message non envoyé")
            return False
        
        start_time = time.time()
        result = self.client.publish(topic, message, qos=1)
        publish_time = (time.time() - start_time) * 1000
        
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        status = "✓" if result.rc == 0 else "✗"
        print(f"[{timestamp}] [MQTT] → {topic} ({publish_time:.1f}ms) {status}")
        
        return result.rc == 0
    
    def get_uid_inscription(self):
        """Récupère l'UID inscription (compatibilité ancienne méthode)"""
        uid = self.uid_inscription
        self.uid_inscription = None
        return uid
    
    def get_uid_transaction(self):
        """Récupère l'UID transaction"""
        uid = self.uid_transaction
        self.uid_transaction = None
        return uid
    
    def set_inscription_callback(self, callback):
        """Définit le callback pour mise à jour immédiate inscription"""
        self.on_uid_inscription_callback = callback
    
    def set_transaction_callback(self, callback):
        """Définit le callback pour mise à jour immédiate transaction"""
        self.on_uid_transaction_callback = callback
    
    def get_stats(self):
        """Retourne les statistiques de performance"""
        avg_latency = sum(self.latency_history) / len(self.latency_history) if self.latency_history else 0
        max_latency = max(self.latency_history) if self.latency_history else 0
        min_latency = min(self.latency_history) if self.latency_history else 0
        
        return {
            "connected": self.connected,
            "broker": self.broker,
            "port": self.port,
            "message_count": self.message_count,
            "last_inscription": self.last_message_time.get("inscription"),
            "last_transaction": self.last_message_time.get("transaction"),
            "avg_latency_ms": round(avg_latency, 1),
            "max_latency_ms": round(max_latency, 1),
            "min_latency_ms": round(min_latency, 1),
            "samples": len(self.latency_history)
        }

mqtt_handler = OptimizedMQTTHandler(broker="broker.hivemq.com", port=1883)