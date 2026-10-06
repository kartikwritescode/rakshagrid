import json
import random
import os
from datetime import datetime, timedelta

def generate_reports():
    reports = []
    
    # Pre-defined names to make synthetic data look realistic
    first_names = [
        "Aarav", "Aditya", "Amit", "Ananya", "Arjun", "Deepak", "Divya", "Ishaan", 
        "Karan", "Kavya", "Manish", "Neha", "Pooja", "Pranav", "Priya", "Rahul", 
        "Rohan", "Sanjay", "Shreya", "Siddharth", "Sneha", "Tanvi", "Varun", "Vikram"
    ]
    last_names = [
        "Sharma", "Verma", "Gupta", "Patel", "Mehta", "Singh", "Kumar", "Joshi", 
        "Reddy", "Rao", "Nair", "Iyer", "Choudhury", "Das", "Sen", "Mishra", 
        "Pandey", "Chatterjee", "Dubey", "Kapoor", "Bahl", "Malhotra", "Goel", "Bansal"
    ]
    
    # Helper to generate random date
    base_date = datetime(2026, 6, 1)
    
    def random_timestamp():
        delta_seconds = random.randint(0, 30 * 24 * 3600)  # within 30 days
        timestamp = base_date + timedelta(seconds=delta_seconds)
        return timestamp.isoformat() + "Z"
    
    def random_phone():
        return f"+91{random.randint(7000000000, 9999999999)}"
        
    def random_upi():
        username = f"{random.choice(first_names).lower()}{random.randint(10, 99)}"
        handle = random.choice(["okaxis", "okhdfc", "ybl", "paytm", "icici"])
        return f"{username}@{handle}"
        
    def random_bank():
        return f"{random.randint(1000000000, 999999999999)}"
        
    def random_device():
        return f"dev_{os.urandom(8).hex()}"

    # ==========================================
    # RING 1: Shared Mule UPI IDs (Mule Ring)
    # 40 reports, paying into 2 shared UPI accounts, sharing 3 scam phone numbers
    # ==========================================
    mule_upis = ["scam_mule_1@okaxis", "scam_mule_2@okicici"]
    scam_phones = ["+919876543210", "+918765432109", "+917654321098"]
    
    for i in range(40):
        victim_id = f"VIC-R1-{i+1:03d}"
        victim_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        reports.append({
            "victimId": victim_id,
            "victimName": victim_name,
            "phoneNumber": random.choice(scam_phones),
            "upiId": random.choice(mule_upis),
            "bankAccount": random_bank(), # victims have unique bank accounts
            "deviceFingerprint": random_device(), # victims have unique devices
            "reportTimestamp": random_timestamp()
        })
        
    # ==========================================
    # RING 2: Shared Scam Device / Emulator Ring (Device Ring)
    # 30 reports, sharing 2 device fingerprints, paying to 3 mule bank accounts
    # ==========================================
    scam_devices = ["device_emul_scammer_alpha", "device_emul_scammer_beta"]
    mule_banks = ["999888777666", "888777666555", "777666555444"]
    
    for i in range(30):
        victim_id = f"VIC-R2-{i+1:03d}"
        victim_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        reports.append({
            "victimId": victim_id,
            "victimName": victim_name,
            "phoneNumber": random_phone(),
            "upiId": random_upi(),
            "bankAccount": random.choice(mule_banks),
            "deviceFingerprint": random.choice(scam_devices),
            "reportTimestamp": random_timestamp()
        })

    # ==========================================
    # RING 3: Dense Cross-linked Collusion Ring (Collusion Ring)
    # 50 reports, multi-hop connection across bank accounts, phone numbers, and devices
    # Group A: 15 victims share Bank X & Phone X
    # Group B: 15 victims share Phone X & Device Y
    # Group C: 20 victims share Device Y & UPI Z
    # ==========================================
    bank_x = "555444333222"
    phone_x = "+919900112233"
    device_y = "device_collusion_hub"
    upi_z = "collusion_mule@ybl"
    
    # Group A
    for i in range(15):
        victim_id = f"VIC-R3A-{i+1:03d}"
        victim_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        reports.append({
            "victimId": victim_id,
            "victimName": victim_name,
            "phoneNumber": phone_x,
            "upiId": random_upi(),
            "bankAccount": bank_x,
            "deviceFingerprint": random_device(),
            "reportTimestamp": random_timestamp()
        })
        
    # Group B
    for i in range(15):
        victim_id = f"VIC-R3B-{i+1:03d}"
        victim_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        reports.append({
            "victimId": victim_id,
            "victimName": victim_name,
            "phoneNumber": phone_x,
            "upiId": random_upi(),
            "bankAccount": random_bank(),
            "deviceFingerprint": device_y,
            "reportTimestamp": random_timestamp()
        })
        
    # Group C
    for i in range(20):
        victim_id = f"VIC-R3C-{i+1:03d}"
        victim_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        reports.append({
            "victimId": victim_id,
            "victimName": victim_name,
            "phoneNumber": random_phone(),
            "upiId": upi_z,
            "bankAccount": random_bank(),
            "deviceFingerprint": device_y,
            "reportTimestamp": random_timestamp()
        })

    # ==========================================
    # NORMAL / ISOLATED REPORTS
    # 80 reports with fully unique values
    # ==========================================
    for i in range(80):
        victim_id = f"VIC-NORM-{i+1:03d}"
        victim_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        reports.append({
            "victimId": victim_id,
            "victimName": victim_name,
            "phoneNumber": random_phone(),
            "upiId": random_upi(),
            "bankAccount": random_bank(),
            "deviceFingerprint": random_device(),
            "reportTimestamp": random_timestamp()
        })

    # Shuffle to simulate random submission order
    random.shuffle(reports)
    
    # Save to file
    output_path = os.path.join(os.path.dirname(__file__), "synthetic_reports.json")
    with open(output_path, "w") as f:
        json.dump(reports, f, indent=2)
        
    print(f"Generated 200 synthetic fraud reports at: {output_path}")

if __name__ == "__main__":
    generate_reports()
