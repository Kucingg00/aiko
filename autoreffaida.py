import json
import os
import random
import string
import time
import requests
from eth_account import Account
from web3 import Web3
from eth_account.messages import encode_defunct
from fake_useragent import UserAgent


class AidaAutoRegistration:
    def __init__(self, debug=False):
        self.base_url = "https://back.aidapp.com"
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": UserAgent().random
        }
        self.web3 = Web3(Web3.HTTPProvider("https://rpc.ankr.com/bsc"))
        self.access_token = None
        self.refresh_token = None
        self.user_info = None
        self.campaign_id = "6b963d81-a8e9-4046-b14f-8454bc3e6eb2"
        self.debug = debug
        
    def generate_wallet(self):
        """Generate random EVM wallet"""
        Account.enable_unaudited_hdwallet_features()
        acct = Account.create()
        return {
            "address": acct.address,
            "private_key": acct.key.hex()
        }

    
    def load_proxies(self):
        """Load proxy settings from proxy.txt"""
        try:
            with open("proxy.txt", "r") as f:
                proxy = f.read().strip()
                return {
                    'http': proxy,
                    'https': proxy
                }
        except Exception as e:
            print(f"⚠️ Error loading proxies: {str(e)}")
            return None
        
    
    def login_with_wallet(self, wallet, ref_code=None):
        """Login dengan wallet dan dapatkan access token"""
        try:
            timestamp = int(time.time() * 1000)
            message = f"MESSAGE_ETHEREUM_{timestamp}:{timestamp}"
            
            private_key = wallet["private_key"]
            message_hash = encode_defunct(text=message)
            signed_message = Account.sign_message(message_hash, private_key)
            signature = signed_message.signature.hex()
            
            login_url = f"{self.base_url}/user-auth/login"
            params = {
                "strategy": "WALLET",
                "chainType": "EVM",
                "address": wallet["address"],
                "token": message,
                "signature": signature
            }
            
            if ref_code:
                params["inviter"] = ref_code

            if self.debug:
                print("\n=== REQUEST LOGIN ===")
                print("URL:", login_url)
                print("Params:", json.dumps(params, indent=4))
                print("======================")

            proxies = self.load_proxies()
            response = requests.get(login_url, params=params, headers=self.headers, proxies=proxies)

            if self.debug:
                print("\n=== RESPONSE LOGIN ===")
                print("Status Code:", response.status_code)
                try:
                    print("Response JSON:", response.json())
                except:
                    print("Response Text:", response.text)
                print("======================")

            if response.status_code == 200:
                data = response.json()
                self.access_token = data["tokens"]["access_token"]
                self.refresh_token = data["tokens"]["refresh_token"]
                self.headers["Authorization"] = f"Bearer {self.access_token}"
                
                wallet["access_token"] = self.access_token
                wallet["refresh_token"] = self.refresh_token
                
                user_info = self.get_user_info()
                if user_info:
                    wallet["user_id"] = user_info["id"]
                    wallet["ref_code"] = user_info["refCode"]
                    wallet["inviter_id"] = user_info["inviterId"]
                
                print(f"✅ Registration berhasil: {wallet['address'][:8]}...{wallet['address'][-6:]}")
                return True
            else:
                print(f"❌ Gagal login: {response.status_code}")
                return False
        except Exception as e:
            print(f"⚠️ Error saat login: {str(e)}")
            return False
    
    def get_user_info(self):
        """Dapatkan informasi pengguna setelah login"""
        try:
            me_url = f"{self.base_url}/user-auth/me"

            if self.debug:
                print("\n=== REQUEST USER INFO ===")
                print("URL:", me_url)
                print("==========================")

            proxies = self.load_proxies()
            response = requests.get(me_url, headers=self.headers, proxies=proxies)

            if self.debug:
                print("\n=== RESPONSE USER INFO ===")
                print("Status Code:", response.status_code)
                try:
                    print("Response JSON:", response.json())
                except:
                    print("Response Text:", response.text)
                print("==========================")

            if response.status_code == 200:
                self.user_info = response.json()
                if self.debug:
                    print(f"✅ Berhasil mendapatkan info pengguna dengan ID: {self.user_info['id']}")
                return self.user_info
            else:
                if self.debug:
                    print(f"❌ Gagal mendapatkan info pengguna: {response.status_code}")
                return None
        except Exception as e:
            if self.debug:
                print(f"⚠️ Error saat mendapatkan info pengguna: {str(e)}")
            return None
    
    def complete_mission(self, mission_id):
        """Menyelesaikan misi"""
        try:
            # Pertama coba pakai endpoint mission-activity
            activity_url = f"{self.base_url}/questing/mission-activity/{mission_id}"
            activity_response = requests.post(activity_url, headers=self.headers)
            
            # Selanjutnya klaim reward
            reward_url = f"{self.base_url}/questing/mission-reward/{mission_id}"
            reward_response = requests.post(reward_url, headers=self.headers)
            
            if reward_response.status_code in [200, 201]:
                return True
            else:
                if self.debug:
                    print(f"❌ Gagal menyelesaikan misi: {mission_id}")
                return False
        except Exception as e:
            if self.debug:
                print(f"⚠️ Error saat menyelesaikan misi: {str(e)}")
            return False
    
    def check_balance(self):
        """Memeriksa saldo pengguna"""
        try:
            balance_url = f"{self.base_url}/scoreboard/campaigns/top/me"
            params = {
                "filter[campaignId]": self.campaign_id
            }
            
            proxies = self.load_proxies()
            balance_response = requests.get(balance_url, params=params, headers=self.headers, proxies=proxies)
            
            if balance_response.status_code == 200:
                balance_data = balance_response.json()
                if self.debug:
                    print(f"Balance Data: {json.dumps(balance_data, indent=4)}")
                return balance_data
            else:
                if self.debug:
                    print(f"❌ Gagal memeriksa saldo: {balance_response.status_code}")
                return None
        except Exception as e:
            if self.debug:
                print(f"⚠️ Error saat memeriksa saldo: {str(e)}")
            return None
    
    def complete_all_tasks(self):
        """Menyelesaikan semua task yang tersedia"""
        print("⏳ Menyelesaikan tasks...")
        
        # Task IDs dari data yang diberikan
        task_ids = {
            "connect_twitter": "f8a1de65-613d-4500-85e9-f7c572af3248",
            "like_tweet": "34ec5840-3820-4bdd-b065-66a127dd1930",
            "join_telegram": "2daf1a21-6c69-49f0-8c5c-4bca2f3c4e40",
            "create_wallet": "df2a34a4-05a9-4bde-856a-7f5b8768889a"
        }
        
        # Menyelesaikan semua task
        for task_name, task_id in task_ids.items():
            self.complete_mission(task_id)
            time.sleep(1)
        
        # Check balance setelah menyelesaikan task
        balance = self.check_balance()
        
        print("✅ Success Complete Tasks..")
        return balance

def process_wallet(ref_code, index, total):
    """Proses satu wallet: buat, login, dan selesaikan task"""
    print(f"\nProcessing Referral [{index}/{total}]")
    
    aida = AidaAutoRegistration(debug=False)
    wallet = aida.generate_wallet()
    
    # Coba login dengan wallet yang baru dibuat
    if aida.login_with_wallet(wallet, ref_code):
        # Menyelesaikan semua task
        aida.complete_all_tasks()
        
        # Menyimpan informasi wallet ke file
        with open("aida_wallets.txt", "a") as f:
            f.write(f"Wallet #{index}\n")
            f.write(f"Address: {wallet['address']}\n")
            f.write(f"Private Key: {wallet['private_key']}\n")
            f.write(f"Ref Code: {wallet.get('ref_code', 'N/A')}\n")
            f.write("-" * 50 + "\n")
        
      #  print(f"💾Data wallet #{index} tersimpan di aida_wallets.txt")
        print(f"💾Referral Sukses!")
        print("===================================")
        return wallet.get('ref_code')
    else:
        print(f"❌ Gagal login untuk wallet #{index}")
        return None

def main():
    print("===================================")
    print("AIDA AUTO REFERRAL & TASK COMPLETER")
    print("         @AirdropFamilyIDN         ")
    print("===================================")

    # Input dari user
    ref_code = input("Masukkan kode referral : ")
    try:
        wallet_count = int(input("Mau berapa Referral?   : "))
    except ValueError:
        print("Input tidak valid, menggunakan default: 1")
        wallet_count = 1
    
    # Buat file untuk menyimpan wallet jika belum ada
    if not os.path.exists("aida_wallets.txt"):
        with open("aida_wallets.txt", "w") as f:
            f.write(f"AIDA WALLETS - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
    
    success_count = 0
    failed_count = 0
    
    # Loop untuk membuat sejumlah wallet
    for i in range(1, wallet_count + 1):
        result = process_wallet(ref_code, i, wallet_count)
        if result:
            success_count += 1
        else:
            failed_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Total Referral Sukses: {success_count}")
    print(f"❌ Total Referral Gagal: {failed_count}")
    print(f"💾Semua data wallet tersimpan di aida_wallets.txt")
    print("=" * 50)

if __name__ == "__main__":
    main()