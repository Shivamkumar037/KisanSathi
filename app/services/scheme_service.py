"""
Scheme Service - Seed government scheme data
"""

from app import db
from app.models.scheme import GovernmentScheme
import json


def seed_scheme_data():
    """Seed all major Indian government schemes for farmers"""

    schemes = [
        {
            'name': 'Pradhan Mantri Kisan Samman Nidhi (PM-Kisan)',
            'short_name': 'PM-Kisan',
            'description': 'Direct income support scheme providing ₹6,000 per year to all landholding farmer families in India, paid in three equal installments of ₹2,000.',
            'description_hindi': 'इस योजना के तहत सभी भूमिधारक किसान परिवारों को प्रति वर्ष ₹6,000 की आय सहायता दी जाती है, जो ₹2,000 की तीन समान किस्तों में दी जाती है।',
            'benefits': json.dumps([
                '₹6,000 per year direct bank transfer',
                'Paid in 3 installments of ₹2,000 each',
                'No middleman - direct to bank account',
                'Available to all landholding farmers'
            ]),
            'eligibility': json.dumps([
                'Small and marginal farmers with cultivable land',
                'Must have Aadhaar card',
                'Must have bank account linked to Aadhaar',
                'Not applicable to government employees, income tax payers'
            ]),
            'documents_required': json.dumps([
                'Aadhaar Card',
                'Land ownership documents / Khasra',
                'Bank passbook',
                'Mobile number linked to Aadhaar'
            ]),
            'how_to_apply': '1. pmkisan.gov.in पर जाएं\n2. "New Farmer Registration" पर क्लिक करें\n3. Aadhaar नंबर और बैंक विवरण भरें\n4. नजदीकी CSC या लेखपाल से मदद लें',
            'official_website': 'https://pmkisan.gov.in',
            'helpline': '155261 / 011-24300606',
            'icon_emoji': '₹',
            'category': 'financial'
        },
        {
            'name': 'Pradhan Mantri Krishi Sinchai Yojana (PMKSY)',
            'short_name': 'PMKSY',
            'description': 'Scheme aimed at improving farm productivity and ensuring better utilization of resources by providing end-to-end irrigation solutions.',
            'description_hindi': 'यह योजना खेत की उत्पादकता में सुधार और संसाधनों के बेहतर उपयोग के लिए छोर-से-छोर सिंचाई समाधान प्रदान करती है।',
            'benefits': json.dumps([
                'Subsidy on drip and sprinkler irrigation systems',
                'Up to 55% subsidy for small farmers',
                'Up to 45% subsidy for other farmers',
                'Improved water use efficiency',
                'Water conservation training'
            ]),
            'eligibility': json.dumps([
                'All categories of farmers',
                'Farmers with own land or lease land for minimum 7 years',
                'Self Help Groups eligible',
                'FPOs and cooperatives also eligible'
            ]),
            'documents_required': json.dumps([
                'Land ownership/lease documents',
                'Aadhaar Card',
                'Bank account details',
                'Passport size photos',
                'Caste certificate (if applicable)'
            ]),
            'how_to_apply': '1. pmksy.gov.in पर जाएं\n2. या नजदीकी कृषि विभाग कार्यालय जाएं\n3. आवेदन पत्र भरें\n4. जरूरी दस्तावेज जमा करें',
            'official_website': 'https://pmksy.gov.in',
            'helpline': '1800-180-1551',
            'icon_emoji': '💧',
            'category': 'irrigation'
        },
        {
            'name': 'Kisan Credit Card (KCC)',
            'short_name': 'KCC',
            'description': 'Credit scheme providing farmers with easy access to credit for agricultural needs including crop cultivation, post-harvest expenses, and allied activities.',
            'description_hindi': 'यह योजना किसानों को फसल उत्पादन, कटाई के बाद के खर्चों और संबद्ध गतिविधियों के लिए आसान ऋण प्रदान करती है।',
            'benefits': json.dumps([
                'Credit limit up to ₹3 lakh at 7% interest rate',
                'Interest subvention of 2% for timely repayment',
                'Additional 3% incentive for prompt payment (effective 4% rate)',
                'No collateral up to ₹1.60 lakh',
                'Insurance coverage included',
                'Valid for 5 years'
            ]),
            'eligibility': json.dumps([
                'All farmers - individual and joint borrowers',
                'Tenant farmers, oral lessees',
                'Self Help Groups of farmers',
                'Must have agricultural land'
            ]),
            'documents_required': json.dumps([
                'Aadhaar Card',
                'Land records / Khasra Khatauni',
                'Passport size photo',
                'Bank account',
                'Address proof'
            ]),
            'how_to_apply': '1. नजदीकी बैंक शाखा (SBI, PNB, Co-operative Bank) जाएं\n2. KCC आवेदन फॉर्म भरें\n3. जमीन के दस्तावेज साथ लाएं\n4. 15 दिन में KCC मिल जाएगी',
            'official_website': 'https://agricoop.nic.in/en/kisancreditcard',
            'helpline': '1800-11-0001',
            'icon_emoji': '💳',
            'category': 'credit'
        },
        {
            'name': 'Pradhan Mantri Fasal Bima Yojana (PMFBY)',
            'short_name': 'PMFBY',
            'description': 'Crop insurance scheme providing financial support to farmers suffering crop loss due to unforeseen events like natural calamities, pests and diseases.',
            'description_hindi': 'यह फसल बीमा योजना किसानों को प्राकृतिक आपदाओं, कीट और बीमारियों के कारण फसल नुकसान पर वित्तीय सहायता देती है।',
            'benefits': json.dumps([
                'Premium: only 2% for Kharif crops',
                'Premium: only 1.5% for Rabi crops',
                '5% for commercial/horticultural crops',
                'Full sum insured coverage',
                'Covers pre-sowing to post-harvest losses',
                'Quick claim settlement via technology'
            ]),
            'eligibility': json.dumps([
                'All farmers growing notified crops',
                'Both loanee and non-loanee farmers',
                'Sharecroppers and tenant farmers',
                'Applicable for notified areas only'
            ]),
            'documents_required': json.dumps([
                'Aadhaar Card',
                'Land records',
                'Bank account passbook',
                'Sowing certificate',
                'Mobile number'
            ]),
            'how_to_apply': '1. pmfby.gov.in पर जाएं या CSC केंद्र जाएं\n2. Kharif के लिए जुलाई 31 तक\n3. Rabi के लिए दिसंबर 31 तक आवेदन करें\n4. बैंक से KCC लोन लेने पर स्वतः नामांकन होता है',
            'official_website': 'https://pmfby.gov.in',
            'helpline': '1800-200-7710',
            'icon_emoji': '🛡️',
            'category': 'insurance'
        },
        {
            'name': 'National Agriculture Market (e-NAM)',
            'short_name': 'e-NAM',
            'description': 'Online trading platform for agricultural commodities connecting farmers directly to buyers across India, eliminating middlemen and ensuring better prices.',
            'description_hindi': 'यह एक ऑनलाइन ट्रेडिंग प्लेटफॉर्म है जो किसानों को पूरे भारत में खरीदारों से सीधे जोड़ता है और बेहतर कीमत सुनिश्चित करता है।',
            'benefits': json.dumps([
                'Direct access to national market',
                'Better price discovery',
                'Transparent bidding process',
                'Online payment directly to farmer',
                'Reduces middlemen exploitation',
                '1000+ mandis connected across India'
            ]),
            'eligibility': json.dumps([
                'All farmers registered with local APMC mandi',
                'Aadhaar and bank account required',
                'Goods must meet quality standards',
                'Available in 585+ districts'
            ]),
            'documents_required': json.dumps([
                'Aadhaar Card',
                'Bank account details',
                'Mobile number',
                'Mandi registration certificate'
            ]),
            'how_to_apply': '1. enam.gov.in पर जाएं\n2. Farmer Registration करें\n3. नजदीकी e-NAM मंडी में जाएं\n4. अपनी उपज की ग्रेडिंग और नीलामी करवाएं',
            'official_website': 'https://enam.gov.in',
            'helpline': '1800-270-0224',
            'icon_emoji': '🏪',
            'category': 'market'
        },
        {
            'name': 'Paramparagat Krishi Vikas Yojana (PKVY)',
            'short_name': 'PKVY',
            'description': 'Scheme promoting organic farming through cluster-based approach, providing financial assistance for certification and market development.',
            'description_hindi': 'यह योजना जैविक खेती को बढ़ावा देती है और प्रमाणीकरण और बाजार विकास के लिए वित्तीय सहायता प्रदान करती है।',
            'benefits': json.dumps([
                '₹50,000 per hectare financial assistance',
                'Organic certification support',
                'Marketing assistance',
                'Training and capacity building',
                'Premium price for organic produce'
            ]),
            'eligibility': json.dumps([
                'Farmers willing to convert to organic farming',
                'Cluster of minimum 50 farmers (20 hectares)',
                'Must follow organic standards for 3 years',
                'Priority to small and marginal farmers'
            ]),
            'documents_required': json.dumps([
                'Land documents',
                'Aadhaar Card',
                'Bank account',
                'Cluster formation certificate'
            ]),
            'how_to_apply': '1. नजदीकी कृषि विभाग से संपर्क करें\n2. 50 किसानों का समूह बनाएं\n3. आवेदन जमा करें\n4. प्रशिक्षण लें और जैविक खेती शुरू करें',
            'official_website': 'https://pgsindia-ncof.gov.in',
            'helpline': '1800-180-1551',
            'icon_emoji': '🌿',
            'category': 'financial'
        },
        {
            'name': 'Soil Health Card Scheme',
            'short_name': 'SHC',
            'description': 'Scheme to issue soil health cards to farmers carrying crop-wise recommendations of nutrients and fertilizers required for individual farms.',
            'description_hindi': 'इस योजना के तहत किसानों को मिट्टी स्वास्थ्य कार्ड दिए जाते हैं जिनमें उनके खेत की मिट्टी के अनुसार उर्वरक सिफारिशें होती हैं।',
            'benefits': json.dumps([
                'FREE soil testing',
                'Crop-wise fertilizer recommendations',
                'Helps reduce fertilizer costs by 10-20%',
                'Improves crop yield',
                'Available every 2 years'
            ]),
            'eligibility': json.dumps([
                'All farmers with agricultural land',
                'No registration fee',
                'Apply at nearest agriculture department office'
            ]),
            'documents_required': json.dumps([
                'Aadhaar Card',
                'Land documents',
                'Soil sample from your farm'
            ]),
            'how_to_apply': '1. नजदीकी कृषि विभाग या Krishi Vigyan Kendra जाएं\n2. अपने खेत की मिट्टी का नमूना दें\n3. 15-30 दिन में मिट्टी स्वास्थ्य कार्ड मिलेगा',
            'official_website': 'https://soilhealth.dac.gov.in',
            'helpline': '1800-180-1551',
            'icon_emoji': '🌱',
            'category': 'financial'
        },
        {
            'name': 'National Food Security Mission (NFSM)',
            'short_name': 'NFSM',
            'description': 'Mission to increase production of rice, wheat, pulses, coarse cereals and commercial crops through area expansion and productivity enhancement.',
            'description_hindi': 'यह मिशन चावल, गेहूं, दालें और व्यावसायिक फसलों का उत्पादन बढ़ाने के लिए क्षेत्र विस्तार और उत्पादकता वृद्धि पर काम करता है।',
            'benefits': json.dumps([
                'Subsidized quality seeds',
                'Farm machinery at subsidized rates',
                'Demonstration of improved practices',
                'Training and capacity building',
                'Assistance for soil amelioration'
            ]),
            'eligibility': json.dumps([
                'Farmers in NFSM districts',
                'Priority to small and marginal farmers',
                'Farmers growing eligible crops'
            ]),
            'documents_required': json.dumps([
                'Aadhaar Card',
                'Land records',
                'Bank account'
            ]),
            'how_to_apply': 'नजदीकी कृषि विभाग या Krishi Vigyan Kendra से संपर्क करें।',
            'official_website': 'https://nfsm.gov.in',
            'helpline': '011-23382012',
            'icon_emoji': '🌾',
            'category': 'financial'
        },
    ]

    added = 0
    for scheme_data in schemes:
        scheme = GovernmentScheme(**scheme_data)
        db.session.add(scheme)
        added += 1

    db.session.commit()
    print(f"✅ Seeded {added} government schemes")
    return added
