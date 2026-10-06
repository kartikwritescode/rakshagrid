# training/rebuild_adversarial.py
import pandas as pd

adversarial_data = [
    # LEGITIMATE BANK ALERTS (Label 0)
    {
        "text": "Hi, this is a notice from Wells Fargo. We noticed a login attempt from a new device in Chicago. If this was you, please authorize it via your mobile banking app. We do not require you to call us or share any code.",
        "label": 0,
        "category": "legitimate_bank_alert",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hello, this is Capital One. We detected a payment of $89 at a Target store. If this is a valid transaction, no action is needed. To report unrecognized activity, please use the card lock feature in your mobile app.",
        "label": 0,
        "category": "legitimate_bank_alert",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hi Rajesh, this is Axis Bank. We blocked a transaction of 5,000 rupees due to insufficient funds. Please check your account balance.",
        "label": 0,
        "category": "legitimate_bank_alert",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "caller: Hello, is this Mr. Patel? receiver: Yes. caller: I am calling from HDFC Bank security. We noticed a charge of 12,000 rupees on your credit card. Did you make this purchase? receiver: Yes, I did. caller: Thank you, we will authorize it. Have a good day.",
        "label": 0,
        "category": "legitimate_bank_alert",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "caller: Hi, this is SBI Fraud Prevention. Did you authorize a wire transfer of 2 lakhs to Rohan? receiver: No, I didn't! caller: I have locked your card. Please log in to your official NetBanking app and reset your password to secure it. receiver: Okay, thank you.",
        "label": 0,
        "category": "legitimate_bank_alert",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "caller: Hello, ICICI Bank customer care. We noticed a double charge for your electricity bill. Did you pay twice? receiver: Yes, by mistake. caller: Please log in to our portal and raise a dispute ticket. We cannot refund it directly over the call. receiver: Okay.",
        "label": 0,
        "category": "legitimate_bank_alert",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },

    # LEGITIMATE DELIVERY NOTICES (Label 0)
    {
        "text": "Hello, this is FedEx. We have a package for you. It requires a signature, and we will attempt delivery tomorrow at 2 PM. You can reschedule this on our website.",
        "label": 0,
        "category": "legitimate_delivery_notice",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hi, this is DHL. Your parcel from London has cleared customs and is on its way. You can track it on our official app using your tracking number.",
        "label": 0,
        "category": "legitimate_delivery_notice",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hello, Delhivery Courier. Your order is out for delivery today. The courier agent will call you before arrival.",
        "label": 0,
        "category": "legitimate_delivery_notice",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "caller: Hello, I am Amit from BlueDart. I have a parcel for you but the house door is locked. Are you home? receiver: No, I am at office. caller: Can I leave it with the security guard? receiver: Yes, please do that. caller: Sure, I will update the status. Thanks.",
        "label": 0,
        "category": "legitimate_delivery_notice",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "caller: Hi, this is DHL. We have a package but the zip code is missing. Can you confirm it? receiver: Yes, it is 110021. caller: Thanks, I have updated the label and it will be delivered tomorrow. receiver: Great.",
        "label": 0,
        "category": "legitimate_delivery_notice",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "caller: Hello, India Post. I have a registered letter for you. receiver: I am not home. caller: Please collect it from the local post office with your ID card. receiver: Okay.",
        "label": 0,
        "category": "legitimate_delivery_notice",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },

    # LEGITIMATE TELECOM NOTICES (Label 0)
    {
        "text": "Hello, this is Airtel. Your prepaid plan is expiring in 3 days. Please recharge your account via the Airtel Thanks App or our official website.",
        "label": 0,
        "category": "legitimate_telecom_notice",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hi, this is Jio. Your mobile data limit has reached 90 percent. You can purchase data add-ons through the MyJio app.",
        "label": 0,
        "category": "legitimate_telecom_notice",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hello, this is Vodafone. Your SIM card Aadhaar verification is pending. Please visit your nearest store with your physical ID card to complete it.",
        "label": 0,
        "category": "legitimate_telecom_notice",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "caller: Hello, this is Jio customer care. We noticed you haven't completed your biometric verification for the new connection. receiver: Can I do it online? caller: No, biometric verification requires your physical presence. Please visit any Jio store with your Aadhaar card. receiver: Okay, I will go today.",
        "label": 0,
        "category": "legitimate_telecom_notice",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "caller: Hello, Airtel support. Your internet connection is reported down. receiver: Yes. caller: We have raised a ticket. A technician will visit your location tomorrow. receiver: Thank you.",
        "label": 0,
        "category": "legitimate_telecom_notice",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "caller: Hi, BSNL support. Your landline bill is overdue. receiver: I will pay it online. caller: Yes, please pay via our official portal. receiver: Okay.",
        "label": 0,
        "category": "legitimate_telecom_notice",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },

    # CHARITY/VOLUNTEER COORDINATION (Label 0)
    {
        "text": "Hi, this is Sarah from the Red Cross. Thank you for volunteering for our weekend blood drive. We need you to arrive at 8 AM at the community center.",
        "label": 0,
        "category": "charity_volunteer_coordination",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hello, this is Amit from Goonj. We are collecting old clothes and blankets for disaster relief. You can drop off your contributions at our local center.",
        "label": 0,
        "category": "charity_volunteer_coordination",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hi, this is Lisa from Oxfam. We are holding a volunteer orientation webinar tomorrow at 6 PM. The link has been sent to your registered email address.",
        "label": 0,
        "category": "charity_volunteer_coordination",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "caller: Hello, is this Rahul? receiver: Yes, speaking. caller: This is Sunita from Goonj. I am calling to confirm your volunteer registration for the collection drive. receiver: Yes, I signed up. caller: Great, we have assigned you to the South Delhi center. Please reach by 9 AM. receiver: Sure, I will be there.",
        "label": 0,
        "category": "charity_volunteer_coordination",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "caller: Hi, this is Rajesh from Red Cross. Thank you for registering to donate blood today. receiver: Yes, what is the location? caller: It is at the community hall near the metro station. Please carry a valid ID card. receiver: Okay, I will reach in an hour.",
        "label": 0,
        "category": "charity_volunteer_coordination",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "caller: Hello, I am calling from Akshaya Patra. We are organizing a fundraising event. Can you help us coordinate the registration desk? receiver: Yes, I would love to. caller: Wonderful, we will email you the registration sheet. receiver: Sounds good.",
        "label": 0,
        "category": "charity_volunteer_coordination",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },

    # CASUAL CONVERSATION (Label 0)
    {
        "text": "hello this is alex from microsoft",
        "label": 0,
        "category": "casual_conversation",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hey Rajesh, are we still on for tennis at 5 PM today? Let me know if you can make it.",
        "label": 0,
        "category": "casual_conversation",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hi Mom, I am heading home now. See you for dinner! Let me know if you need me to pick up groceries.",
        "label": 0,
        "category": "casual_conversation",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "caller: Hey, did you get the movie tickets? receiver: Yes, booked them for the 7 PM show. caller: Awesome, let's meet outside the theater by 6:45. receiver: Sounds good, see you there.",
        "label": 0,
        "category": "casual_conversation",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "caller: Hi Mom, are you home? receiver: Yes, just got back from the market. caller: Can you check if my black jacket is in the cupboard? receiver: Yes, let me check. Yes, it is here. caller: Thanks, I will pick it up tomorrow.",
        "label": 0,
        "category": "casual_conversation",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "caller: Hey Rajesh, do you know where I left my charger? receiver: I think it's on the dining table. caller: Ah, found it. Thanks, see you at work. receiver: Bye.",
        "label": 0,
        "category": "casual_conversation",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },

    # TECH SUPPORT SCAM (Label 1)
    {
        "text": "This is Microsoft support. We detected a severe security breach on your computer. Please go to your browser and download AnyDesk immediately so we can fix it.",
        "label": 1,
        "category": "tech_support_scam",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hello, this is Windows Security Department. Your computer has sent multiple error reports indicating a Trojan virus infection. Please download TeamViewer to allow our technician to clean it.",
        "label": 1,
        "category": "tech_support_scam",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hi, this is Apple Support. We noticed suspicious activity on your iCloud account. Please download UltraViewer to verify your identity and secure your files.",
        "label": 1,
        "category": "tech_support_scam",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "caller: Hello, this is Microsoft Support. We received an automated error report from your Windows PC. Is your computer nearby? receiver: Yes, what's wrong? caller: Your computer is infected with a Trojan virus. Please open your browser, search for TeamViewer, and download it immediately so I can clean your system. receiver: Okay, downloading it now.",
        "label": 1,
        "category": "tech_support_scam",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "caller: Hi, this is Apple Security calling. We noticed a security breach on your device. receiver: Oh no, what should I do? caller: Please download AnyDesk from the App Store and share the connection code with me. I will verify your account security. receiver: Downloading it.",
        "label": 1,
        "category": "tech_support_scam",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "caller: This is McAfee Security. Your computer is infected with malware. receiver: How did it happen? caller: You visited an unsafe website. Please install AnyDesk immediately so we can block the hackers. receiver: Okay.",
        "label": 1,
        "category": "tech_support_scam",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },

    # UTILITY DISCONNECT SCAM (Label 1)
    {
        "text": "This is the Electric Department calling. Your bill of 4,500 rupees is past due. If you do not pay right now via this link, we will disconnect your power in the next 15 minutes.",
        "label": 1,
        "category": "utility_disconnect_scam",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hello, this is the Gas Supply Board. Your monthly gas bill is unpaid. We have sent a technician to disconnect your line. To cancel this, please transfer the money to our verification account immediately.",
        "label": 1,
        "category": "utility_disconnect_scam",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hi, this is the Water Department. Your water connection will be disconnected within the next 30 minutes due to unpaid arrears of 8,000 rupees. Pay right now via UPI.",
        "label": 1,
        "category": "utility_disconnect_scam",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "caller: Hello, is this Rajesh? receiver: Yes, speaking. caller: This is Rohan from State Electricity Board. Your bill is overdue and we are disconnecting your power in 10 minutes. receiver: But I paid it yesterday! caller: We didn't receive it. You must pay 4,500 rupees right now to our temporary verification account or your power goes off. receiver: Okay, please don't disconnect. Tell me the account details.",
        "label": 1,
        "category": "utility_disconnect_scam",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "caller: Hi, this is Gas Supply. Your payment failed and we are cutting your line today. receiver: How can I pay? caller: Please transfer the money to our UPI ID GasAuthority@ybl immediately. The technician is at your building. receiver: Doing it now.",
        "label": 1,
        "category": "utility_disconnect_scam",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "caller: This is Water Department. Your connection will be cut off in 15 minutes due to unpaid bill. receiver: I will pay online. caller: No, our online system is down. You must pay via our quick payment link right now. receiver: Send the link.",
        "label": 1,
        "category": "utility_disconnect_scam",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },

    # CREDENTIAL HARVESTING SCAM (Label 1)
    {
        "text": "Hello, this is your bank security officer. We are updating our database. Can you confirm your password and the security question answer of your favorite place?",
        "label": 1,
        "category": "credential_harvesting_scam",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hi, this is the credit card department. We noticed a suspicious attempt to access your profile. Please provide your online banking user id and password so we can verify your identity.",
        "label": 1,
        "category": "credential_harvesting_scam",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hello, this is telecom support. We are upgrading your SIM card security. Please share the 6-digit OTP code sent to your phone to activate the new security features.",
        "label": 1,
        "category": "credential_harvesting_scam",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "caller: Hello, this is Bank Verification Department. We are verifying your profile. Can you tell me your online banking user ID? receiver: Yes, it is Patel123. caller: Thank you. I have sent a verification code to your phone. Can you please read it to me? receiver: It is 554433. caller: Perfect, your profile is verified.",
        "label": 1,
        "category": "credential_harvesting_scam",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "caller: Hi, this is HDFC Support. We are updating our KYC database. Please tell me your current ATM PIN. receiver: Why do you need my PIN? caller: It is for database synchronization. We cannot update your card profile without it. receiver: My PIN is 4321. caller: Thank you.",
        "label": 1,
        "category": "credential_harvesting_scam",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "caller: This is Google support. We detected a login attempt. Can you tell me the code sent to your mobile? receiver: It is 987654. caller: Thank you, we have secured your account.",
        "label": 1,
        "category": "credential_harvesting_scam",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },

    # ADDITIONAL ADV PATTERNS (Label 1 / 0)
    {
        "text": "This is Officer Kumar from the Delhi Police Headquarters. A package containing illegal narcotics and passports was intercepted under your name. You must stay on this video call for digital arrest.",
        "label": 1,
        "category": "digital_arrest",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "This is a final notice from the Customs Department at Mumbai Airport. A parcel in your name contains illegal substances. You will face legal action unless you cooperate right now.",
        "label": 1,
        "category": "customs_impersonation",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "caller: This is Delhi Police Headquarters. A case of money laundering has been registered under your name. You are under digital arrest. You must transfer funds to the verification account immediately or go to jail. receiver: Oh my god, what should I do? caller: Please stay on this call and do not disconnect. receiver: Okay, I am listening.",
        "label": 1,
        "category": "digital_arrest",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "You have won a lottery of 25 lakhs from KBC! To claim your prize money, please transfer 15,000 rupees for registration fees.",
        "label": 1,
        "category": "lottery_scam",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Dear customer, your KYC is suspended. Please click on the link in the message to update your Aadhaar card within 24 hours.",
        "label": 1,
        "category": "kyc_scam",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hello, this is a call from Netflix support. Your payment method failed and your subscription is paused. Can we update your credit card details over the phone?",
        "label": 1,
        "category": "subscription_phishing",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "caller: Hello, is this Mrs. Gupta? I'm calling from your child's school. They had a minor fall on the playground and are in the medical room. They are fine, but can you pick them up? receiver: Oh, thank you. I will come right now. caller: Sure, see you soon. receiver: Bye.",
        "label": 0,
        "category": "legitimate_emergency",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "Hi, this is a follow-up from the doctor's office. Your lab test results are ready. Please log in to your portal to view them.",
        "label": 0,
        "category": "legitimate_healthcare",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hi, this is the society security gate. A visitor named Amit is here to see you. Should I let him in?",
        "label": 0,
        "category": "legitimate_gate",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "caller: Hi, this is Rajesh calling from your local electric department. Your electricity bill is unpaid and we will disconnect your power in the next 30 minutes unless you pay right now. receiver: I paid it. caller: No, our system shows unpaid. receiver: Okay, I am sending the payment.",
        "label": 1,
        "category": "utility_disconnect_scam",
        "source": "handwritten_adversarial",
        "format": "dialogue"
    },
    {
        "text": "We have sent a link to your phone to confirm your address. Please click on it and verify.",
        "label": 0,
        "category": "borderline_link_verification",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hi, I am calling from the Prime Minister Relief Fund. We are raising money to help flood victims. You can donate via our official website.",
        "label": 0,
        "category": "legitimate_charity",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hello, this is a standard automated system verification call. We need to verify if you wish to maintain your active account status. Please press 1 to confirm.",
        "label": 0,
        "category": "legitimate_verification",
        "source": "handwritten_adversarial",
        "format": "single"
    },
    {
        "text": "Hey, did you send me that link on WhatsApp? It says I need to enter my verification pin. Is it safe or is it a scam?",
        "label": 0,
        "category": "casual_conversation",
        "source": "handwritten_adversarial",
        "format": "single"
    }
]

df = pd.DataFrame(adversarial_data)
df.to_csv("data/adversarial_eval.csv", index=False)
print(f"Successfully rebuilt data/adversarial_eval.csv with {len(df)} placeholders-free, balanced examples.")

