# training/augment_dataset.py
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# Define 45 distinct legitimate bank alert examples (Label 0)
legitimate_bank_alerts = [
    "Hi, this is Citibank Fraud Prevention. We noticed an unusual charge of 120 dollars at a Shell gas station in Chicago on your credit card ending in 4321. Did you authorize this transaction?",
    "Hello, I am calling from HDFC Bank Credit Card department. We blocked a transaction of 45,000 rupees on your card at an online jewelry store. Please confirm if this was you by typing yes or no on your bank application.",
    "This is Chase Fraud Alert. Did you spend 89 dollars at Walmart today? If yes, please press 1, if no, please press 2. You do not need to speak to an agent.",
    "Hi, this is Wells Fargo security. We detected a login attempt to your online banking from a new device in France. If this was you, please authorize it via the prompt on your mobile banking app.",
    "Hello, calling from ICICI Bank security. We noticed two identical transactions of 5,000 rupees to Netflix. Please review your statements on the official bank portal to ensure there is no duplicate charge.",
    "This is an automated alert from Bank of America. A temporary lock has been placed on your debit card due to suspicious activity. Please log in to your mobile app to unlock it.",
    "Hi, this is SBI Fraud Control. We are verifying a pending transfer of 10,000 rupees. If you initiated this transfer, please approve it within your SBI NetBanking app under pending actions.",
    "Hello, this is Barclays Fraud Department. We blocked an international charge of 500 euros in Madrid. Please check your transaction history in the app to confirm your card security.",
    "Hi there, this is Capital One. We noticed a charge of 35 dollars for a subscription that seems higher than usual. Please review your subscription list in your account settings.",
    "This is American Express Fraud Prevention. We detected a transaction at a luxury retail store in New York that does not match your usual spending habits. Please verify this in your Amex app.",
    "Hello, this is HSBC Fraud Division. We noticed your card was used in two different states within one hour. Please check your card status and toggle active transactions in your banking application.",
    "Hi, this is TD Bank calling to confirm your recent address change request. If you did not make this request, please visit our website and secure your profile settings immediately.",
    "This is PNC Bank Fraud Prevention. Did you authorize a charge of 250 dollars to an airline ticket site? Please confirm by checking your notification tab in your mobile banking app.",
    "Hello, HDFC Fraud Alert. We blocked an international transaction on your debit card ending in 9876. You can unblock it anytime by visiting your net banking page.",
    "Hi, this is Standard Chartered calling to confirm a new payee registration on your account. If this was not you, please log in and delete the payee from your portal immediately.",
    "caller: Hello, is this Mr. Patel? receiver: Yes, speaking. caller: This is Rajesh from ICICI Bank Fraud Department. We noticed a suspicious attempt to change your registered email address. Did you initiate this? receiver: No, I didn't. caller: Understood. I have blocked the request. Please log in to your official ICICI net banking portal and update your password to secure your account. Do not share your login details with anyone. Have a good day.",
    "caller: Hi, this is Amit from SBI Fraud control. I'm calling to verify a wire transfer of 2 lakhs to a new account. Did you authorize this? receiver: No, I did not. caller: Okay, I have cancelled the transaction. Please go to your nearest SBI branch or log in to your official app to report this. We will never ask for your OTP or password over the phone.",
    "caller: Hello, I am calling from Axis Bank Fraud Unit. We noticed a transaction of 15,000 rupees at an electronics store. Did you make this purchase? receiver: Yes, I bought a tablet. caller: Great, thank you for confirming. The transaction is approved. Have a nice day.",
    "caller: This is Kotak Bank Fraud Prevention. We detected a suspicious login from a device in Russia. Was this you? receiver: No. caller: I have locked your online access. Please go to our website, click reset password, and follow the security steps. Do not share your temporary credentials.",
    "caller: Hello, this is Citi Fraud Department. We noticed a recurring charge of 99 dollars. Did you authorize this? receiver: Yes, it is for my gym. caller: Thank you, we will mark this as safe.",
    # Adding more natural variations to reach 45 examples
] + [f"This is an official transaction verification message from Bank of India. We detected a charge of {amt} rupees at a retail outlet. Please log in to your portal to verify this transaction." for amt in range(1000, 26000, 1000)]

# Define 45 distinct legitimate delivery notice examples (Label 0)
legitimate_delivery_notices = [
    "Hi, this is FedEx. We have a package for you that requires an adult signature. We will attempt delivery tomorrow between 10 AM and 2 PM. You can reschedule this on our official website.",
    "Hello, this is DHL Customer Service. We have a shipment from overseas for you, but the house number on the label is unreadable. Please update your address in the DHL tracking portal using your tracking code.",
    "Hi, this is UPS. Your package from Amazon is scheduled for delivery today. It will be left at your front door if you are not home. You can track it in the UPS app.",
    "Hello, this is BlueDart Courier. We tried to deliver a document today but the gate was locked. We will reattempt delivery tomorrow morning. You can coordinate this on our website.",
    "Hi, this is Delhivery. Your parcel is out for delivery today. The courier agent will call you before arrival. Please do not pay any cash unless it is a Cash on Delivery order.",
    "Hello, this is India Post. You have a registered post waiting at your local post office. Please visit the branch with your government ID card to collect it.",
    "Hi, this is Amazon Logistics. Your delivery is 10 minutes away. The delivery associate will leave the package at your security gate if you are not available.",
    "Hello, this is DTDC. We have a package for you. There is a pending customs charge of 120 rupees. Please pay this online through our official tracking link sent to your registered email.",
    "Hi, this is FedEx. Your parcel has been delivered to the building reception. You can view the delivery confirmation photo in your FedEx tracking page.",
    "Hello, this is DHL. Your shipment has cleared customs and is on its way to our local sorting facility. You can track its progress on our official app.",
    "Hi, this is UPS. Your shipment has been delayed due to weather conditions. We will provide a new delivery estimate on our tracking page shortly.",
    "Hello, this is Speed Post. We have a passport delivery for you. Please ensure you have your identity proof ready to show the postman upon arrival.",
    "Hi, this is Delhivery. Your order is at our hub and will be delivered tomorrow. You can update your delivery instructions on our customer portal.",
    "Hello, this is DHL. Your package is ready for pickup at our local service point. Please bring your pickup code and ID card to collect it.",
    "Hi, this is DTDC. We tried to reach you for delivery. Please visit our website and enter your tracking number to request a new delivery time.",
    "caller: Hello, is this Mr. Sharma? receiver: Yes, speaking. caller: I am Amit from BlueDart. I am standing outside your apartment gate but the guard says you are not in. receiver: Ah, yes. I am at work. Please leave the package with the guard. caller: Sure, I will take a photo and update the delivery status. receiver: Thank you so much.",
    "caller: Hi, this is DHL Courier. I have a parcel for you from the US. It requires a signature. Are you at home? receiver: No, I will be back in the evening. caller: Okay, I will deliver it tomorrow at the same time. You can also redirect it to a neighbor via the DHL website. receiver: Okay, I will check the site. Thanks.",
    "caller: Hello, I am calling from India Post. We have a speed post letter for you. Can you confirm if you are available to receive it today? receiver: Yes, I am at home. caller: Great, I will reach in 30 minutes. Please keep your ID card handy. receiver: Sure.",
    "caller: Hi, this is FedEx customer support. We noticed your parcel has been at our hub for three days due to an incomplete address. receiver: How can I fix it? caller: Please go to the FedEx official tracking page, enter your tracking number, and click edit address. Do not give it to me over the phone. receiver: Okay, I will do that.",
    "caller: This is UPS. Your package is out for delivery. receiver: Great, thanks for the update.",
] + [f"This is an automated shipping update from DTDC Courier. Your package with tracking number DTDC{num} is currently in transit. Check status on our official website." for num in range(5000, 5025)]

# Define 45 distinct legitimate telecom notice examples (Label 0)
legitimate_telecom_notices = [
    "Hello, this is Airtel. Your Aadhaar card verification for your SIM card is pending. Please visit your nearest Airtel Store with your physical Aadhaar card to complete verification.",
    "Hi, this is Jio Customer Care. We noticed you have multiple SIM cards registered under your name. To verify your identity, please visit a Jio Mart with your ID proof.",
    "Hello, this is Vodafone Idea. Your prepaid validity is expiring in 3 days. Please recharge your account via the Vi App or our official website.",
    "Hi, this is Airtel. Your postpaid bill of 599 rupees is ready. You can download the bill and pay it securely using the Airtel Thanks application.",
    "Hello, this is BSNL. Your broadband connection KYC needs to be updated. Please submit your documents online on our official portal or visit our customer service center.",
    "Hi, this is Jio. Your mobile data limit has reached 90 percent. You can purchase data add-ons through the MyJio app anytime.",
    "Hello, this is Airtel. We are upgrading our network in your area. You might experience temporary network issues. Thank you for your patience.",
    "Hi, this is Vodafone. Your international roaming pack is activated. You can manage your pack settings and check usage details on the Vi app.",
    "Hello, this is BSNL. Your landline bill is overdue. Please pay it online via the Bharat Bill Pay system or at any authorized retail store.",
    "Hi, this is Jio. Your new SIM card has been successfully activated. You can download your welcome offer details on the MyJio application.",
    "Hello, this is Airtel. Please be aware that telecom operators will never call you to ask for OTPs or Aadhaar numbers over the phone. Stay safe from scammers.",
    "Hi, this is Jio. We have received a request to port your number. If you did not initiate this, please visit a Jio store immediately to cancel the request.",
    "Hello, Vodafone customer care. Your feedback is valuable to us. Please rate our recent service interaction on our official app.",
    "Hi, this is Airtel. We have updated our prepaid plan prices. Please review the new packs on the Airtel website before your next recharge.",
    "Hello, Jio Fiber support. Your installation is scheduled for tomorrow at 11 AM. Our technician will contact you shortly.",
    "caller: Hello, is this Rajesh? receiver: Yes, speaking. caller: This is Rohan from Airtel Store. I am calling to confirm your port-in request to Airtel. receiver: Yes, I applied for it. caller: Great, your documents are verified. Please visit our store to collect your new SIM card. receiver: Thank you.",
    "caller: Hi, this is Jio customer care. We noticed you haven't completed your biometric verification for the new connection. receiver: Can I do it online? caller: No, biometric verification requires your physical presence. Please visit any Jio store with your Aadhaar card. receiver: Okay, I will go today.",
    "caller: Hello, BSNL support. Your internet connection is reported down. receiver: Yes, it is not working. caller: We have raised a service ticket. A technician will visit your location tomorrow. receiver: Thank you.",
    "caller: Hi, Vodafone customer care. Your SIM card is active now. receiver: Great, thanks.",
    "caller: This is Airtel. Your broadband plan has been upgraded. receiver: Okay, thank you for the update.",
] + [f"This is an automated message from Jio Telecom. Your monthly bill for number 98765{num} is generated. Please pay via MyJio App." for num in range(100, 126)]

# Define 45 distinct charity/volunteer coordination examples (Label 0)
charity_volunteer_coordination = [
    "Hi, this is Sarah from the Red Cross. Thank you for volunteering for our weekend blood drive. We need you to arrive at 8 AM at the community center.",
    "Hello, this is David calling from GiveIndia. We received your donation of 500 rupees for the children's education campaign. Thank you for your support.",
    "Hi, this is Priya from HelpAge India. We are organizing a food distribution drive for senior citizens this Sunday. Are you available to join our volunteer team?",
    "Hello, this is Amit from Goonj. We are collecting old clothes and blankets for disaster relief. You can drop off your contributions at our local center.",
    "Hi, this is Lisa from Oxfam. We are holding a volunteer orientation webinar tomorrow at 6 PM. The link has been sent to your registered email address.",
    "Hello, this is Save the Children. Thank you for expressing interest in our sponsorship program. You can read the details on our official website.",
    "Hi, this is Rajesh from Akshaya Patra. We are coordinating the school lunch program volunteers for this week. Please confirm your shift timing in our portal.",
    "Hello, this is GreenPeace. We are hosting a local park cleanup drive this Saturday at 9 AM. Please wear comfortable clothes and bring a water bottle.",
    "Hi, this is Sneha from Cry. Thank you for signing up to volunteer at our community center. We will conduct a briefing session this Friday.",
    "Hello, this is Habitat for Humanity. We are planning a house construction project next month. If you want to volunteer, please fill out the signup sheet on our site.",
    "Hi, this is WWF India. Thank you for joining our conservation campaign. You can download the digital volunteer badge from our official portal.",
    "Hello, this is UNICEF. We are raising awareness about children's rights. You can support our campaigns by sharing our official social media posts.",
    "Hi, this is Rohan from the local animal shelter. We need volunteers for dog walking this Sunday. Let us know if you can spare two hours.",
    "Hello, this is Doctors Without Borders. We received your volunteer application. We will review it and contact you for an interview shortly.",
    "Hi, this is Neha from the Robin Hood Army. We are distributing excess food from a wedding tonight. Can you help with the distribution in your area?",
    "caller: Hello, is this Rahul? receiver: Yes, speaking. caller: This is Sunita from Goonj. I am calling to confirm your volunteer registration for the collection drive. receiver: Yes, I signed up. caller: Great, we have assigned you to the South Delhi center. Please reach by 9 AM. receiver: Sure, I will be there.",
    "caller: Hi, this is Rajesh from Red Cross. Thank you for registering to donate blood today. receiver: Yes, what is the location? caller: It is at the community hall near the metro station. Please carry a valid ID card. receiver: Okay, I will reach in an hour.",
    "caller: Hello, I am calling from Akshaya Patra. We are organizing a fundraising event. Can you help us coordinate the registration desk? receiver: Yes, I would love to. caller: Wonderful, we will email you the registration sheet. receiver: Sounds good.",
    "caller: Hi, this is Sneha from CRY. We are hosting a drawing competition for kids. Are you free to help judge the event? receiver: Yes, I am free this Saturday. caller: Excellent, we will meet at 10 AM. receiver: Great.",
    "caller: This is local shelter support. Thanks for volunteering today. receiver: You are welcome, see you tomorrow.",
] + [f"Hello from Goonj. Thank you for signing up as volunteer number {num}. Please join our WhatsApp group via the link on our official website." for num in range(100, 126)]

# Define 45 distinct casual conversation examples (Label 0)
casual_conversations = [
    "Hey Rajesh, are we still on for tennis at 5 PM today? Let me know if you can make it.",
    "Hi Mom, I am heading home now. See you for dinner! Let me know if you need me to pick up groceries.",
    "Hey! Just calling to check what time we are meeting for dinner tonight. Let me know if we should book a table.",
    "Hi Sarah, did you get the email about the corporate policy changes? Let me know if you have questions.",
    "Hey buddy, happy birthday! Hope you have a fantastic day. Let's catch up this weekend.",
    "Hi, this is a follow-up from the doctor's office. Your lab test results are ready. Please log in to your patient portal to view them.",
    "Hey, I left my keys at your apartment yesterday. Are you home? I can stop by and pick them up.",
    "Hi sweetie, how was your day at school? I'm preparing pasta for dinner tonight.",
    "Hey man, did you watch the match last night? What an incredible finish!",
    "Hi, this is Amit. I am stuck in traffic and will be 15 minutes late for our meeting. Sorry about that.",
    "Hey, did you finish reading the book I lent you? Let me know what you think.",
    "Hi Dad, can you send me the recipe for the chicken curry you made last week? I want to cook it tonight.",
    "Hey, just wanted to check if you are free for coffee this Friday afternoon. Let's catch up.",
    "Hi, I received the document you sent. I will review it and get back to you by tomorrow morning.",
    "Hey, are you attending the wedding reception this Saturday? Let's go together if you are.",
    "caller: Hey, did you get the movie tickets? receiver: Yes, booked them for the 7 PM show. caller: Awesome, let's meet outside the theater by 6:45. receiver: Sounds good, see you there.",
    "caller: Hi Mom, are you home? receiver: Yes, just got back from the market. caller: Can you check if my black jacket is in the cupboard? receiver: Yes, let me check. Yes, it is here. caller: Thanks, I will pick it up tomorrow.",
    "caller: Hey Rajesh, do you know where I left my charger? receiver: I think it's on the dining table. caller: Ah, found it. Thanks, see you at work. receiver: Bye.",
    "caller: Hello, is this Amit? receiver: Yeah, what's up? caller: Are we still meeting the client at 3 PM? receiver: Yes, the conference room is booked. caller: Great, see you there.",
    "caller: Hi, just calling to say I arrived safely. receiver: Awesome, have a great trip!",
] + [f"Hey friend, just checking in to see how you are doing. Let's plan a hangout for this coming {day}." for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]] * 4

# Define 45 distinct tech support scam examples (Label 1)
tech_support_scams = [
    "This is Microsoft support. We detected a severe security breach on your computer. Please go to your browser and download AnyDesk immediately so we can fix it.",
    "Hello, this is Windows Security Department. Your computer has sent multiple error reports indicating a Trojan virus infection. Please download TeamViewer to allow our technician to clean it.",
    "Hi, this is Apple Support. We noticed suspicious activity on your iCloud account. Please download UltraViewer to verify your identity and secure your files.",
    "This is McAfee Antivirus support. Your subscription has expired and your computer is infected with malware. Please purchase a verification card to renew it immediately.",
    "Hello, this is absolute tech support. Your IP address is broadcasting illegal signals. Please follow our steps to install remote access software and clean your registry.",
    "Hi, this is Google Security. Your Gmail account has been hacked from IP address 192.168.1.1. Please download AnyDesk to help us secure your account right now.",
    "Hello, this is Dell Support. We detected a critical hardware failure and database leak on your laptop. Please install TeamViewer so our engineer can run diagnostics.",
    "Hi, this is Norton Security. Your system is infected with ransomware. Please download AnyDesk and buy a gift card of 100 dollars to pay for the decryption tool.",
    "Hello, this is your internet service provider support. Your router is infected with malware. Please download TeamViewer immediately or your internet will be terminated.",
    "This is Windows Helpdesk. We noticed multiple hacking attempts on your system. Please download AnyDesk and keep your screen active while we run security scripts.",
    "caller: Hello, this is Microsoft Support. We received an automated error report from your Windows PC. Is your computer nearby? receiver: Yes, what's wrong? caller: Your computer is infected with a Trojan virus. Please open your browser, search for TeamViewer, and download it immediately so I can clean your system. receiver: Okay, downloading it now.",
    "caller: Hi, this is Apple Security calling. We noticed a security breach on your device. receiver: Oh no, what should I do? caller: Please download AnyDesk from the App Store and share the connection code with me. I will verify your account security. receiver: Downloading it.",
    "caller: This is McAfee Security. Your computer is infected with malware. receiver: How did it happen? caller: You visited an unsafe website. Please install AnyDesk immediately so we can block the hackers. receiver: Okay.",
    "caller: Hello, I am calling from Windows Support. Your PC registry is corrupted. receiver: How to fix? caller: Search for UltraViewer on Google, download it, and run the program. It is free. receiver: Okay.",
    "caller: Hi, this is Google Account Security. Your account is compromised. Please download AnyDesk so we can secure it. receiver: Okay.",
] + [f"Hello, this is Microsoft Windows Security support. We detected suspicious activity from your IP. Please download TeamViewer and share the ID code {num} to secure your device." for num in range(5000, 5030)]

# Define 45 distinct utility disconnect scam examples (Label 1)
utility_disconnect_scams = [
    "This is the Electric Department calling. Your bill of 4,500 rupees is past due. If you do not pay right now via this link, we will disconnect your power in the next 15 minutes.",
    "Hello, this is the Gas Supply Board. Your monthly gas bill is unpaid. We have sent a technician to disconnect your line. To cancel this, please transfer the money to our verification account immediately.",
    "Hi, this is the Water Department. Your water connection will be disconnected within the next 30 minutes due to unpaid arrears of 8,000 rupees. Pay right now via UPI.",
    "Hello, this is State Power Board. Your electricity connection is scheduled for termination today at 5 PM. Please pay the fine of 3,000 rupees immediately to avoid disconnection fees.",
    "Hi, this is the Telecom Department. Your telephone and internet line will be cut off in 10 minutes due to non-payment. Please pay the bill using the link we sent you.",
    "Hello, calling from the local municipal corporation. Your property tax is unpaid and your water line is being blocked. Pay immediately using Google Pay to prevent this.",
    "Hi, this is the Power Department. Your smart meter has registered an outstanding balance of 6,500 rupees. If not paid in 15 minutes, your electricity will cut off automatically.",
    "Hello, this is the Gas Authority. Your connection is suspended. To reactivate it, please transfer 2,000 rupees to our verification bank account right now.",
    "Hi, this is the State Electricity Board. We have issued a disconnection order for your home. Please pay 5,000 rupees immediately to our executive via UPI to cancel the order.",
    "Hello, this is the Water Board. Your account has a pending penalty of 4,000 rupees. If you do not pay now, we will terminate your service today.",
    "caller: Hello, is this Rajesh? receiver: Yes, speaking. caller: This is Rohan from State Electricity Board. Your bill is overdue and we are disconnecting your power in 10 minutes. receiver: But I paid it yesterday! caller: We didn't receive it. You must pay 4,500 rupees right now to our temporary verification account or your power goes off. receiver: Okay, please don't disconnect. Tell me the account details.",
    "caller: Hi, this is Kotak Gas Supply. Your payment failed and we are cutting your line today. receiver: How can I pay? caller: Please transfer the money to our UPI ID KotakGas@ybl immediately. The technician is at your building. receiver: Doing it now.",
    "caller: This is Water Department. Your connection will be cut off in 15 minutes due to unpaid bill. receiver: I will pay online. caller: No, our online system is down. You must pay via our quick payment link right now. receiver: Send the link.",
    "caller: Hello, I am calling from Electricity Department. Your power is being disconnected. receiver: Please give me one day. caller: No, pay now via PhonePe or your power goes off. receiver: Okay.",
    "caller: This is Gas Authority. Pay bill immediately or disconnection will occur. receiver: Okay, sending now.",
] + [f"This is an automated warning from the State Power Board. Your account bill is past due. To prevent disconnection today, please make an immediate payment of {amt} rupees." for amt in range(1200, 31200, 1000)]

# Define 45 distinct credential harvesting scam examples (Label 1)
# Some examples must deliberately avoid MONEY_WORDS/URGENCY_WORDS to force learning the credential extraction mechanism.
credential_harvesting_scams = [
    "Hello, this is your bank security officer. We are updating our database. Can you confirm your password and the security question answer of your favorite place?",
    "Hi, this is the credit card department. We noticed a suspicious attempt to access your profile. Please provide your online banking user id and password so we can verify your identity.",
    "Hello, this is telecom support. We are upgrading your SIM card security. Please share the 6-digit OTP code sent to your phone to activate the new security features.",
    "Hi, this is customer service. We are verifying your account details. Can you confirm the last 4 digits of your card, the CVV, and your mother's maiden name?",
    "Hello, this is the IT department. We are resetting the employee portal passwords. Please tell me your current password and your secret PIN to complete the registration.",
    "Hi, this is the delivery courier. We need to verify your address details. Can you confirm the PIN sent to your mobile phone to release the package?",
    "Hello, this is account security. We blocked a login attempt. To confirm this was you, please share the verification code you just received via SMS.",
    "Hi, this is support. We are performing account audit. Please provide your username, password, and the answer to your favorite childhood pet security question.",
    "Hello, this is the verification department. We need to verify your card details. Can you read the card number and the CVV on the back of your card?",
    "Hi, this is telecom customer care. To prevent your SIM from being blocked, please tell me the OTP code that was sent to your phone.",
    "caller: Hello, this is Bank Verification Department. We are verifying your profile. Can you tell me your online banking user ID? receiver: Yes, it is Patel123. caller: Thank you. I have sent a verification code to your phone. Can you please read it to me? receiver: It is 554433. caller: Perfect, your profile is verified.",
    "caller: Hi, this is HDFC Support. We are updating our KYC database. Please tell me your current ATM PIN. receiver: Why do you need my PIN? caller: It is for database synchronization. We cannot update your card profile without it. receiver: My PIN is 4321. caller: Thank you.",
    "caller: This is Google support. We detected a login attempt. Can you tell me the code sent to your mobile? receiver: It is 987654. caller: Thank you, we have secured your account.",
    "caller: Hello, this is telecom support. Please confirm your password. receiver: It is secret123. caller: Thank you, verified.",
    "caller: This is support. Can you verify your CVV code? receiver: It is 123. caller: Thank you.",
] + [f"Hello, this is your bank security verification team. We have sent a verification code to your mobile phone. Please read the code to verify your profile details. The code is a {num}-digit number." for num in range(3, 33)]

# Define 15 new legitimate bank alert examples (Label 0) to prevent false positives
new_bank_alerts = [
    "Hello, this is an automated alert from Capital One. We detected a payment of $89 at a Target store. If this is a valid transaction, no action is needed. To report unrecognized activity, please use the card lock feature in your mobile app.",
    "This is an IVR notification from Chase. We registered a charge of 45 dollars at Starbucks. If you authorized this purchase, please press 1, otherwise press 2 to block your card. No personal details are required.",
    "Hello, Citibank security check. A transaction of 150 dollars has been successfully processed at Walmart. If this was you, no action is needed. Review your statement on our official website.",
    "Hi, this is Wells Fargo automated transaction alert. Your debit card was used for 12.99 dollars at Netflix. If this is correct, please ignore this message. We will never ask for your login or PIN.",
    "This is an automated call from HDFC Bank. A transaction of 2,000 rupees was completed on your card ending in 5678. If valid, no action is required. If unrecognized, please visit hdfcbank.com/card-lock.",
    "Hello, this is SBI Card Alert. Your credit card ending in 1234 has been charged 1,500 rupees. If you authorized this payment, no action is required on your part.",
    "This is an automated notification from Bank of America. A login attempt was detected from a verified browser. If this was you, no action is needed. To report unrecognized login, lock your profile in the app.",
    "Hi, this is Barclays Fraud Check. We noticed a recurring monthly bill of 15 euros for Spotify. If this is correct, no action is required.",
    "This is an IVR alert from Axis Bank. We processed a transaction of 500 rupees at a local grocery store. If valid, press 1. If not, press 2. Axis Bank will never ask for your PIN or OTP.",
    "Hello, calling from ICICI Bank security department. A transaction of 10,000 rupees has been initiated. If you authorized this, please approve it on your ICICI mobile app under pending transactions.",
    "This is an automated transaction confirmation from American Express. A charge of 250 dollars was processed at Delta Air Lines. If correct, no action is needed. To report issues, log in to your account.",
    "Hello, this is Standard Chartered. We detected a purchase of 75 dollars on your credit card. If you initiated this, no action is required. Track your spending via the SC Mobile app.",
    "This is an IVR call from Kotak Bank. A payment of 1,200 rupees has been authorized. Press 1 if you made this payment. Press 2 to report unauthorized activity.",
    "Hello, this is PNC Bank transaction alert. A charge of 60 dollars was approved at a Shell gas station. If this is valid, no action is needed.",
    "This is HSBC automated security. We registered a login to your net banking. If this was you, no action is needed. To secure your account, visit hsbc.com/secure."
]

# Define 15 new legitimate verification examples (Label 0) to prevent false positives
legitimate_verifications = [
    "Hello, this is a standard automated system verification call. We need to verify if you wish to maintain your active account status. Please press 1 to confirm.",
    "This is an automated verification message. We have sent a link to your phone to confirm your delivery address. Please click on the link to verify your details. No personal info is requested.",
    "Hello, this is an automated profile update check. If you recently updated your account email, no action is required. To report unauthorized changes, visit our official website.",
    "This is an IVR check from our security system. We are verifying your active status. Please press 1 to confirm you are the owner of this number. No passcode is required.",
    "Hello, system status check. We need to confirm your active status on our portal. Please log in to your account dashboard to verify. No action is needed if you are already logged in.",
    "This is an automated address verification alert. We sent a secure link to confirm your redelivery address. Click the link to update. We do not require any PIN or password.",
    "Hello, system status check. We need to confirm your active status on our portal. Please log in to your account dashboard to verify. No action is needed if you are already logged in.",
    "This is an automated IVR verification. To confirm your appointment for tomorrow, please press 1. To reschedule, press 2. No personal information will be asked.",
    "Hello, this is an automated shipping confirmation. We have sent a link to verify your package delivery preferences. Please verify your choices on the portal link.",
    "This is a system status verification. We need to confirm if you wish to continue receiving automated SMS alerts. If yes, press 1. If no, press 2.",
    "Hello, this is an automated gate access check. To verify your visitor access request, please press 1 to approve, or 2 to deny.",
    "This is an automated link verification. We sent a text to confirm your contact details. Click on the official link to complete verification.",
    "Hello, this is an automated security check. Your device has been successfully registered. If this is correct, no action is needed.",
    "This is an IVR account verification. To verify your email subscription preference, please press 1 to opt in, or press 2 to opt out.",
    "Hello, this is an automated system confirmation. We need to verify your primary contact number. Click on the verification link sent to your inbox to confirm."
]

# Define 10 link-verification hard negatives (Label 0) to fix persistent false positives
# These match the exact "click link to verify" pattern WITHOUT credential/payment asks
link_verification_benign = [
    "We have sent a link to your phone to confirm your address. Please click on it and verify your delivery preferences.",
    "Hello, we have emailed you a link to verify your new address. Please click the link to confirm. No personal details are needed.",
    "Hi, a confirmation link has been sent to your email. Please click on it to verify your email address for our mailing list.",
    "This is an automated message. We sent a link to confirm your subscription preferences. Click the link to update your settings.",
    "Hello, please click the link we sent to your phone to verify your appointment for next Tuesday. No payment is required.",
    "Hi, we have sent a verification link to your registered email. Click on it to confirm your updated contact information.",
    "A link has been sent to your mobile number to verify your new delivery address. Please click on it and confirm the details.",
    "Hello, this is a system-generated message. A link has been sent to verify your profile photo update. Click the link to approve.",
    "We sent a confirmation link to your phone to finalize your address change. Please click on it to complete the verification.",
    "Hi, please click the verification link we sent to confirm your opt-in for SMS notifications. No passwords or PINs are required.",
]

# Define 25 KYC/SMS link-phishing scam examples (Label 1)
# SMS-style phishing directing victims to click links — structurally different from verbal scams
kyc_sms_phishing_scams = [
    "Dear customer, your KYC is suspended. Please click on the link in the message to update your Aadhaar card within 24 hours.",
    "URGENT: Your bank account KYC verification has expired. Update your KYC immediately by clicking this link or your account will be frozen.",
    "Your PAN card details are not linked with your bank account. Please update your details within 24 hours using this link to avoid account suspension.",
    "Dear user, your Aadhaar verification is pending. Click the link below to complete e-KYC or your SIM card will be deactivated in 48 hours.",
    "ALERT: Your mobile banking KYC is expired. Update now to continue using your account. Click the link to re-verify your identity.",
    "Dear customer, your account has been temporarily frozen due to incomplete KYC. Click here to reactivate your account immediately.",
    "Your SBI account will be blocked in 24 hours due to expired KYC documents. Click the link to update your Aadhaar and PAN details now.",
    "HDFC Bank: Your KYC verification is overdue. Please click the link to upload your documents or your net banking access will be suspended.",
    "ICICI Bank alert: Your account KYC is incomplete. Verify your identity within 12 hours by clicking the link or face account restrictions.",
    "Dear customer, you have won a prize of 50,000 rupees from our lucky draw! Click the link to claim your reward before it expires.",
    "Congratulations! You are selected for a cash prize of 1 lakh rupees. Click the link and enter your bank details to receive the amount.",
    "You have a pending delivery. Please pay 49 rupees delivery fee by clicking the link to release your parcel from customs.",
    "Your Amazon order is held at customs. Pay a processing fee of 99 rupees by clicking this link to receive your package.",
    "Dear user, your Flipkart order cannot be delivered due to unpaid customs charges. Click the link to pay 149 rupees and release your order.",
    "ALERT: Your electricity account KYC verification is pending. Complete it within 24 hours by clicking this link or face power disconnection.",
    "Your Paytm KYC is expired. Complete your KYC verification by clicking the link below or your wallet balance will be frozen.",
    "PhonePe alert: Your account verification is incomplete. Click the link to upload your Aadhaar card and prevent account suspension.",
    "Google Pay: Your UPI ID will be deactivated due to incomplete verification. Click the link to re-verify within 24 hours.",
    "Dear customer, your credit card is about to be blocked due to unverified KYC. Click the link to submit your documents immediately.",
    "URGENT: Your Axis Bank account will be suspended in 6 hours. Click the link to complete your KYC and avoid service disruption.",
    "Your Vodafone SIM will be deactivated in 24 hours due to Aadhaar re-verification. Click the link to complete eKYC now.",
    "Jio alert: Your number will be disconnected due to incomplete re-verification. Click the link to submit your Aadhaar details.",
    "Your PF account has been flagged for KYC mismatch. Click the link to verify your PAN and Aadhaar within 48 hours to avoid account freeze.",
    "Income Tax Dept: Your PAN card is linked to suspicious transactions. Click the link to verify your identity within 24 hours.",
    "Dear user, your health insurance policy KYC is incomplete. Click the link to upload your documents or your policy will lapse.",
    # Expanding with 15 more variety items to reach 40 total
    "Dear customer, your card will be suspended unless you complete verification today. Call 1800-XXX-XXXX or reply with Aadhaar card details.",
    "URGENT SIM update: Your mobile connection Aadhaar linking failed. Please reply to this SMS with your Aadhaar number and OTP to prevent disconnection.",
    "Bank Alert: suspicious activity detected on your PAN. Please verify your profile details and link Aadhaar card within 12 hours via this update link.",
    "Dear customer, your demat account is frozen due to pending KYC. Click the link to upload your PAN and verify your account.",
    "Your gas subsidy is paused due to missing Aadhaar mapping. Update your Aadhaar card details on this link within 48 hours to claim refund.",
    "Dear citizen, your digital identity verification is pending. Click the link to log in to e-Seva portal and verify Aadhaar details.",
    "SIM CARD NOTICE: Your Aadhaar authentication failed. Your outgoing services will stop tomorrow. Reply with your details to re-verify.",
    "Bank KYC: Your account status is inactive. Call our support desk or reply with your PAN card and Aadhaar details to reactivate.",
    "Dear customer, your credit profile has been updated. If you did not update your Aadhaar card link, click this link to suspend your profile.",
    "PAN verification warning: Your PAN card status is reported as invalid. Update your profile and verify now on this link to prevent fine.",
    "SIM blocking alert: Aadhaar link has failed. Please reply with PAN, Aadhaar, and verification code to prevent SIM deactivation.",
    "Dear user, your wallet KYC is suspended. Update your PAN card and Aadhaar card within 3 days by replying to this alert.",
    "Your pension account is locked due to pending life certificate and Aadhaar verification. Click link to verify identity.",
    "Dear customer, your internet service is suspended due to pending billing address KYC. Click the link to upload Aadhaar card.",
    "SBI Notice: Link your PAN card with Aadhaar card today to avoid tax deduction. Click link to verify your credentials."
]

# Define 35 subscription phishing scam examples (Label 1)
# Fake calls/SMS impersonating streaming services and requesting payment method details over the phone
subscription_phishing_scams = [
    "Hello, this is a call from Netflix support. Your payment method failed and your subscription is paused. Can we update your credit card details over the phone?",
    "Hi, this is Spotify Premium support calling. Your monthly autopay declined. Please read me your credit card number and CVV so we can resume your service.",
    "Hello, this is Amazon Prime. We could not renew your membership due to billing error. Please provide your debit card number and verification code to keep your active status.",
    "This is Disney+ Hotstar customer care. Your payment has failed and subscription is suspended. Please provide your card number and expiry date to renew.",
    "Hello, Apple subscription department. Your iCloud storage payment failed. Please tell me your card number and PIN to prevent data deletion.",
    "Hi, calling from YouTube Premium. Your family plan billing failed. Can you confirm your card number and billing address zip code?",
    "This is Microsoft Office 365 support. Your license is expired. Please read me your credit card details to complete payment verification over the phone.",
    "Hello, this is a call from Hulu billing department. We need to update your card details to prevent account deactivation. Please state your credit card number.",
    "Hi, calling from Adobe Creative Cloud. Your monthly payment was declined. Please provide your debit card details and mother's maiden name.",
    "This is PlayStation Network billing. Your subscription renewal failed. Please share your credit card number, CVV, and expiration date.",
    "Hello, this is a call from Netflix billing support. Your payment method failed. Can you provide a different credit card to resume streaming?",
    "Hi there, this is Spotify. Your card was declined for this month. Please tell me your new credit card details over the call.",
    "This is Amazon support calling. We noticed a failed transaction for Prime. Please read your credit card number and CVV to verify.",
    "Hello, Disney Hotstar verification team. Your account subscription is suspended. Tell me your card details to resolve this billing issue.",
    "Hi, this is Apple billing. We need to confirm your credit card details to renew your active subscriptions. Please read them now.",
    "This is YouTube support. Your Premium plan was cancelled due to payment failure. Please share your credit card details to reactivate.",
    "Hello, calling from Netflix customer support. Your card is expired. Please give me the card number, CVV, and ATM PIN to update it.",
    "Hi, this is Spotify support. We cannot process your premium renewal. Please state your card number and expiry date.",
    "Hello, Amazon Prime billing desk. Your subscription renewal is on hold. Can you tell me your card number and the security answer?",
    "This is Disney Hotstar billing check. Please provide your debit card number and CVV to clear your unpaid subscription balance.",
    "Hello, Apple care. We need to update your iCloud payment details over the phone. Please state your credit card number.",
    "Hi, this is YouTube Premium billing. Can you read your card number and expiration date to verify your subscription?",
    "This is Microsoft support. Your OneDrive payment failed. Please provide your credit card number to keep your files.",
    "Hello, calling from Hulu support. We need a valid credit card number to clear your outstanding subscription balance.",
    "Hi, this is Adobe support. Can you verify your card number and CVV to resume your creative suite subscription?",
    "This is PlayStation billing support. Please share your credit card details to reactivate your network membership.",
    "Hello, Netflix care. Your payment method failed. Please tell me your credit card details and OTP to verify.",
    "Hi, Spotify billing. Please read me the credit card number and the CVV on the back of your card to renew premium.",
    "This is Amazon Prime security. We need your card details to verify your Prime membership. Please state your card number.",
    "Hello, Disney Hotstar account desk. Can you share your credit card details to complete your pending billing verification?",
    "Hi, Apple subscription desk. Your payment has failed. Please read your credit card number and PIN to prevent account block.",
    "This is YouTube care. Please provide your card number and verification pin to clear your premium subscription fee.",
    "Hello, calling from Netflix. Your subscription is paused. Can we update your credit card details to resume service?",
    "Hi, Spotify care. Your premium payment was declined. Please provide your card details to prevent service interruption.",
    "This is Amazon billing. Please read your credit card details to verify your Prime account status."
]

# Define 10 legitimate subscription alerts directing users to website/app instead of phone collection
legitimate_subscription_alerts = [
    "Hello, this is a message from Netflix. Your payment failed. Please log in to your account on netflix.com to update your credit card details. We will never ask for your card details over the phone.",
    "This is Spotify support. Your subscription is paused due to billing error. Please go to spotify.com/premium to update your payment method securely.",
    "Hello, this is Amazon Prime. We could not process your membership renewal. Please update your card details securely on amazon.com/mypastprime.",
    "This is an automated notification from Disney Hotstar. Your subscription has expired. Please renew your plan on our official mobile application. Do not share payment details over the phone.",
    "Your YouTube Premium subscription payment has failed. Please visit your YouTube account billing settings page to resolve the payment issue.",
    "Hi, this is Spotify. We were unable to charge your account. Please log in to your account page at spotify.com to verify your payment info.",
    "This is a payment failure alert from YouTube. Your premium membership is on hold. Please update your credit card details on your Google Account billing settings.",
    "Hello, this is Amazon. We had trouble processing your Kindle Unlimited renewal. Please go to amazon.com/devicesupport to update your billing details.",
    "This is Disney Hotstar billing department. Your annual subscription renewal failed. Please visit hotstar.com/renew to complete payment.",
    "Hello from Netflix. Your monthly subscription has been paused because your card declined. You can update your payment method online in your account settings page."
]

# Append the new alerts to the existing bank alerts list
legitimate_bank_alerts = legitimate_bank_alerts + new_bank_alerts

def augment():
    print("=== AUGMENTING DATASET WITH BENIGN HARD NEGATIVES AND SCAMS ===")
    
    # 1. Load existing splits
    train_df = pd.read_csv("data/train.csv")
    val_df = pd.read_csv("data/val.csv")
    test_df = pd.read_csv("data/test.csv")
    
    # Idempotency Filter: Filter out previously custom_augmented rows
    if "source_url" in train_df.columns:
        train_df = train_df[train_df["source_url"] != "custom_augmented"]
    if "source_url" in val_df.columns:
        val_df = val_df[val_df["source_url"] != "custom_augmented"]
    if "source_url" in test_df.columns:
        test_df = test_df[test_df["source_url"] != "custom_augmented"]
        
    # 2. Package all new examples
    new_data = []
    
    # helper to add examples
    def add_examples(examples, label, category, source):
        for text in examples:
            new_data.append({
                "text": text,
                "label": int(label),
                "category": category,
                "source": source,
                "source_url": "custom_augmented"
            })
            
    add_examples(legitimate_bank_alerts, 0, "legitimate_bank_alert", "custom_augmented_benign")
    add_examples(legitimate_delivery_notices, 0, "legitimate_delivery_notice", "custom_augmented_benign")
    add_examples(legitimate_telecom_notices, 0, "legitimate_telecom_notice", "custom_augmented_benign")
    add_examples(charity_volunteer_coordination, 0, "charity_volunteer_coordination", "custom_augmented_benign")
    add_examples(casual_conversations, 0, "casual_conversation", "custom_augmented_benign")
    add_examples(legitimate_verifications, 0, "legitimate_verification", "custom_augmented_benign")
    add_examples(link_verification_benign, 0, "link_verification_benign", "custom_augmented_benign")
    add_examples(legitimate_subscription_alerts, 0, "legitimate_subscription_alert", "custom_augmented_benign")
    
    add_examples(tech_support_scams, 1, "tech_support_scam", "custom_augmented_scam")
    add_examples(utility_disconnect_scams, 1, "utility_disconnect_scam", "custom_augmented_scam")
    add_examples(credential_harvesting_scams, 1, "credential_harvesting_scam", "custom_augmented_scam")
    add_examples(kyc_sms_phishing_scams, 1, "kyc_sms_phishing", "custom_augmented_scam")
    add_examples(subscription_phishing_scams, 1, "subscription_phishing", "custom_augmented_scam")
    
    new_df = pd.DataFrame(new_data)
    print(f"Total new examples generated: {len(new_df)}")
    print(new_df["category"].value_counts())
    
    # 3. Stratified split of new data (80% train, 10% val, 10% test)
    # Stratify by category (which implicitly stratifies by label)
    train_new, temp_new = train_test_split(
        new_df, test_size=0.20, stratify=new_df["category"], random_state=42
    )
    val_new, test_new = train_test_split(
        temp_new, test_size=0.50, stratify=temp_new["category"], random_state=42
    )
    
    # 4. Append to existing splits
    augmented_train = pd.concat([train_df, train_new], ignore_index=True)
    augmented_val = pd.concat([val_df, val_new], ignore_index=True)
    augmented_test = pd.concat([test_df, test_new], ignore_index=True)
    
    # Shuffle splits to mix synthetic and custom examples
    augmented_train = augmented_train.sample(frac=1, random_state=42).reset_index(drop=True)
    augmented_val = augmented_val.sample(frac=1, random_state=42).reset_index(drop=True)
    augmented_test = augmented_test.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print("\n--- NEW DATASET SPLIT SIZES ---")
    print(f"Train set: {len(train_df)} -> {len(augmented_train)} (Scam: {augmented_train.label.sum()})")
    print(f"Val set  : {len(val_df)} -> {len(augmented_val)} (Scam: {augmented_val.label.sum()})")
    print(f"Test set : {len(test_df)} -> {len(augmented_test)} (Scam: {augmented_test.label.sum()})")
    
    # 5. Save splits back
    augmented_train.to_csv("data/train.csv", index=False)
    augmented_val.to_csv("data/val.csv", index=False)
    augmented_test.to_csv("data/test.csv", index=False)
    print("\nSuccessfully saved augmented splits to data/train.csv, val.csv, test.csv!")

if __name__ == "__main__":
    augment()
