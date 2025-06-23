import requests
import random
import string
import threading
from web3 import Web3
from bs4 import BeautifulSoup
from faker import Faker
from colorama import init, Fore, Style

# Initialize colorama
init()

# Configuration
SUCCESS_FILE = "account-validate.txt"
MAX_THREADS = 5  # Adjust based on your system capabilities

# Constants
COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola",
    "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria",
    "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados",
    "Belarus", "Belgium", "Belize", "Benin", "Bhutan",
    "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei",
    "Bulgaria", "Burkina Faso", "Burundi", "Côte d'Ivoire", "Cabo Verde",
    "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad",
    "Chile", "China", "Colombia", "Comoros", "Congo (Congo-Brazzaville)",
    "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czechia (Czech Republic)",
    "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica",
    "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea",
    "Eritrea", "Estonia", "Eswatini (fmr. Swaziland)", "Ethiopia", "Fiji",
    "Finland", "France", "Gabon", "Gambia", "Georgia",
    "Germany", "Ghana", "Greece", "Grenada", "Guatemala",
    "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Holy See",
    "Honduras", "Hungary", "Iceland", "India", "Indonesia",
    "Iran", "Iraq", "Ireland", "Israel", "Italy",
    "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya",
    "Kiribati", "Kuwait", "Kyrgyzstan", "Laos", "Latvia",
    "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein",
    "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia",
    "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania",
    "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco",
    "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar (formerly Burma)",
    "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand",
    "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia",
    "Norway", "Oman", "Pakistan", "Palau", "Palestine State",
    "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines",
    "Poland", "Portugal", "Qatar", "Romania", "Russia",
    "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa",
    "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia",
    "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia",
    "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan",
    "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden",
    "Switzerland", "Syria", "Tajikistan", "Tanzania", "Thailand",
    "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia",
    "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine",
    "United Arab Emirates", "United Kingdom", "United States of America", "Uruguay", "Uzbekistan",
    "Vanuatu", "Venezuela", "Vietnam", "Yemen", "Zambia",
    "Zimbabwe"
]

DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com", "icloud.com"]

class AccountGenerator:
    def __init__(self):
        self.fake = Faker()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "Sec-GPC": "1",
        })

    def generate_random_email(self):
        """Generate a random email address"""
        name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 10)))
        domain = random.choice(DOMAINS)
        return f"{name}@{domain}"

    def generate_random_country(self):
        """Generate a random country"""
        return random.choice(COUNTRIES)

    def generate_random_name(self):
        """Generate a random name"""
        return self.fake.name()

    def generate_ethereum_wallet(self):
        """Generate a new Ethereum wallet"""
        w3 = Web3()
        account = w3.eth.account.create()
        return account.address, account.key.hex()

    def get_request_verification_token(self):
        """Get the anti-forgery token from the registration page"""
        url = "https://coinkove.com/"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            token = soup.find('input', {'name': '__RequestVerificationToken'})['value']
            return token, response.cookies
        except Exception as e:
            print(Fore.RED + f"Error getting token: {str(e)}" + Style.RESET_ALL)
            return None, None

    def save_success_registration(self, data):
        """Save successful registration to file"""
        with open(SUCCESS_FILE, "a") as f:
            f.write(f"Generated new Ethereum wallet:\n")
            f.write(f"Address: {data['walletaddress']}\n")
            f.write(f"Private Key: {data['private_key']} (keep this secure!)\n\n")
            f.write(f"Name: {data['Fullname']}\n")
            f.write(f"Email: {data['emailaddress']}\n")
            f.write(f"Country: {data['country']}\n")
            f.write(f"Wallet: {data['walletaddress']}\n")
            f.write("-"*50 + "\n\n")

    def submit_registration(self, wallet_address, private_key, token, cookies):
        """Submit the registration form"""
        url = "https://coinkove.com/?handler=Subscribe"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://coinkove.com",
            "Referer": "https://coinkove.com/",
        }
        
        payload = {
            "Fullname": self.generate_random_name(),
            "emailaddress": self.generate_random_email(),
            "country": self.generate_random_country(),
            "walletaddress": wallet_address,
            "__RequestVerificationToken": token,
            "handler": "Subscribe"
        }
        
        print(Fore.CYAN + "\nSubmitting with following data:" + Style.RESET_ALL)
        print(f"Name: {payload['Fullname']}")
        print(f"Email: {payload['emailaddress']}")
        print(f"Country: {payload['country']}")
        print(f"Wallet: {wallet_address[:10]}...{wallet_address[-6:]}")
        
        try:
            response = self.session.post(url, headers=headers, data=payload, cookies=cookies, timeout=15)
            
            if self.check_success(response):
                print(Fore.GREEN + "\n✓ Registration successful!" + Style.RESET_ALL)
                print("You have been added to the waitlist!\n")
                self.save_success_registration({
                    **payload,
                    "private_key": private_key
                })
                return True
            else:
                print(Fore.RED + "\n✗ Registration failed!" + Style.RESET_ALL)
                return False
        except Exception as e:
            print(Fore.RED + f"\n✗ Registration error: {str(e)}" + Style.RESET_ALL)
            return False

    def check_success(self, response):
        """Check if registration was successful"""
        return "You have been added to the waitlist successfully!" in response.text

    def create_account(self):
        """Handle single account creation"""
        # Generate wallet
        wallet_address, private_key = self.generate_ethereum_wallet()
        print(Fore.YELLOW + "\nGenerated new Ethereum wallet:" + Style.RESET_ALL)
        print(f"Address: {wallet_address}")
        print(f"Private Key: {private_key[:10]}...{private_key[-6:]}")
        
        # Get token
        token, cookies = self.get_request_verification_token()
        if not token:
            print(Fore.RED + "Failed to get token, please try again" + Style.RESET_ALL)
            return
        
        # Submit registration
        self.submit_registration(wallet_address, private_key, token, cookies)

    def create_multiple_accounts(self, num_accounts):
        """Handle multiple account creation with threading"""
        print(Fore.YELLOW + f"\nStarting creation of {num_accounts} accounts..." + Style.RESET_ALL)
        
        threads = []
        success_count = 0
        
        for i in range(num_accounts):
            # Generate wallet
            wallet_address, private_key = self.generate_ethereum_wallet()
            
            # Get token
            token, cookies = self.get_request_verification_token()
            if not token:
                print(Fore.RED + "Failed to get token, retrying..." + Style.RESET_ALL)
                continue
            
            # Create thread
            t = threading.Thread(
                target=lambda: self.submit_registration(wallet_address, private_key, token, cookies) and globals().update(success_count=success_count+1)
            )
            threads.append(t)
            t.start()
            
            # Limit active threads
            while threading.active_count() > MAX_THREADS:
                pass
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        print(Fore.GREEN + f"\nCompleted! Successfully created {success_count}/{num_accounts} accounts" + Style.RESET_ALL)
        print(f"Details saved to {SUCCESS_FILE}")

def display_banner():
    """Display program banner"""
    print(Fore.BLUE + r"""
██████╗ ██████╗ ██╗███╗   ██╗██╗  ██╗ ██████╗ ██╗   ██╗███████╗
██╔════╝██╔═══██╗██║████╗  ██║██║ ██╔╝██╔═══██╗██║   ██║██╔════╝
██║     ██║   ██║██║██╔██╗ ██║█████╔╝ ██║   ██║██║   ██║█████╗  
██║     ██║   ██║██║██║╚██╗██║██╔═██╗ ██║   ██║╚██╗ ██╔╝██╔══╝  
╚██████╗╚██████╔╝██║██║ ╚████║██║  ██╗╚██████╔╝ ╚████╔╝ ███████╗
 ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝   ╚═══╝  ╚══════╝
    """ + Style.RESET_ALL)
    print(Fore.YELLOW + "Coinkove Auto Registration @ByAdfmidn" + Style.RESET_ALL)
    print(Fore.CYAN + "="*50 + Style.RESET_ALL)

def main():
    display_banner()
    generator = AccountGenerator()
    
    while True:
        try:
            choice = input("\nCreate (1) Single account or (2) Multiple accounts? (1/2): ")
            if choice == '1':
                generator.create_account()
                break
            elif choice == '2':
                num_accounts = int(input("How many accounts to create? (1-1000): "))
                if 1 <= num_accounts <= 1000:
                    generator.create_multiple_accounts(num_accounts)
                    break
                print(Fore.RED + "Please enter a number between 1 and 1000" + Style.RESET_ALL)
            else:
                print(Fore.RED + "Please enter 1 or 2" + Style.RESET_ALL)
        except ValueError:
            print(Fore.RED + "Please enter a valid number" + Style.RESET_ALL)

if __name__ == "__main__":
    main()