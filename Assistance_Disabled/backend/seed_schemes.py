import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.modules.schemes.models import GovernmentScheme

schemes_data = [
    {
        "name": "ADIP Scheme (Assistance to Disabled Persons)",
        "description": "Provides financial assistance to disabled persons of low income for purchase of aids and appliances to improve mobility, communication and self-reliance.",
        "disability_type": "physical",
        "eligibility": "Indian citizen with 40%+ disability. Monthly income below Rs. 20,000. Age 5-65 years.",
        "how_to_apply": "1. Visit nearest DDRC. 2. Fill application form. 3. Submit disability certificate and income proof. 4. Aids distributed in camp or sent directly.",
        "documents_required": "Disability certificate (40%+), Income certificate, Age proof, Passport photo, Bank details",
        "official_link": "https://disabilityaffairs.gov.in/content/page/adip-scheme.php"
    },
    {
        "name": "Divyangjan Scholarship Scheme",
        "description": "Scholarships for students with disabilities from class 9 to PhD level. Covers tuition fees, maintenance and book allowance.",
        "disability_type": "physical",
        "eligibility": "Student with 40%+ disability. Family income below Rs. 2.5 lakh per annum.",
        "how_to_apply": "1. Register on scholarships.gov.in. 2. Fill scholarship application. 3. Upload documents. 4. Submit before deadline.",
        "documents_required": "Disability certificate, Income certificate, Marksheet, Bonafide certificate, Bank account, Aadhar",
        "official_link": "https://scholarships.gov.in"
    },
    {
        "name": "NHFDC Loan Scheme",
        "description": "Loans at concessional interest rates for disabled persons for self-employment and income generating activities.",
        "disability_type": "physical",
        "eligibility": "40%+ disability. Age 18-55 years. Income below Rs. 3 lakh per annum.",
        "how_to_apply": "1. Contact State Channelising Agency. 2. Submit loan application with business plan. 3. Loan sanctioned within 30 days.",
        "documents_required": "Disability certificate, Aadhar, Income proof, Business plan, Bank statement (6 months)",
        "official_link": "https://nhfdc.nic.in"
    },
    {
        "name": "Free Braille Books and Materials",
        "description": "Free Braille books, talking books and educational materials to visually impaired students through NIVH.",
        "disability_type": "visual",
        "eligibility": "Visually impaired students in any recognized school or college.",
        "how_to_apply": "1. Contact NIVH Dehradun. 2. Submit application with disability certificate. 3. Materials sent by post.",
        "documents_required": "Visual disability certificate, School enrollment proof, Aadhar, Address proof",
        "official_link": "https://nivh.gov.in"
    },
    {
        "name": "Assistance for Purchase of DAISY Players",
        "description": "DAISY players provided free or subsidized to visually impaired persons to listen to audio books and educational content.",
        "disability_type": "visual",
        "eligibility": "Visual impairment of 40%+. Monthly income below Rs. 20,000.",
        "how_to_apply": "1. Apply through DDRC. 2. Submit disability and income certificates. 3. Device provided in distribution camps.",
        "documents_required": "Visual disability certificate (40%+), Income certificate, Aadhar, Bank details, Passport photo",
        "official_link": "https://disabilityaffairs.gov.in/content/page/adip-scheme.php"
    },
    {
        "name": "Free Hearing Aid Scheme (ADIP)",
        "description": "Free hearing aids to persons with hearing impairment under the ADIP scheme.",
        "disability_type": "hearing",
        "eligibility": "Hearing impairment of 40%+. Monthly income below Rs. 20,000. Age 5+.",
        "how_to_apply": "1. Visit DDRC or AYJNISHD. 2. Audiological assessment done. 3. Hearing aid fitted and provided free.",
        "documents_required": "Hearing disability certificate, Income certificate, Aadhar, Age proof, Passport photo",
        "official_link": "https://ayjnishd.gov.in"
    },
    {
        "name": "Sign Language Interpreter Scheme",
        "description": "Trained sign language interpreters for hearing impaired persons for government services, legal and medical use.",
        "disability_type": "hearing",
        "eligibility": "Person with hearing impairment requiring communication support.",
        "how_to_apply": "1. Contact ISLRTC. 2. Submit request with purpose and date. 3. Interpreter assigned.",
        "documents_required": "Hearing disability certificate, Aadhar, Purpose of requirement",
        "official_link": "https://islrtc.nic.in"
    },
    {
        "name": "Cochlear Implant Programme",
        "description": "Financial assistance for cochlear implant surgery for children with profound hearing loss below age 5.",
        "disability_type": "hearing",
        "eligibility": "Children below 5 years with profound bilateral hearing loss. Family income below Rs. 6 lakh.",
        "how_to_apply": "1. Get audiological evaluation from government hospital. 2. Apply through AYJNISHD Mumbai. 3. Surgery at empanelled hospitals.",
        "documents_required": "Audiological reports, Age proof, Income certificate, Aadhar of child and parents",
        "official_link": "https://ayjnishd.gov.in"
    },
    {
        "name": "National Trust Schemes (Autism, CP, MR, MD)",
        "description": "Support for persons with Autism, Cerebral Palsy, Mental Retardation and Multiple Disabilities including residential, respite and day care.",
        "disability_type": "mental",
        "eligibility": "Persons with Autism, Cerebral Palsy, Mental Retardation or Multiple Disabilities.",
        "how_to_apply": "1. Register on thenationaltrust.gov.in. 2. Apply for specific scheme. 3. Benefits through registered organizations.",
        "documents_required": "Disability certificate, Aadhar, Income proof, Medical reports, Guardian identity proof",
        "official_link": "https://thenationaltrust.gov.in"
    },
    {
        "name": "Niramaya Health Insurance Scheme",
        "description": "Health insurance up to Rs. 1 lakh per year for persons with Autism, CP, Mental Retardation and Multiple Disabilities at very low premium.",
        "disability_type": "mental",
        "eligibility": "Persons with Autism, CP, Mental Retardation or Multiple Disabilities. BPL: Rs. 250 premium, Others: Rs. 500 per year.",
        "how_to_apply": "1. Visit National Trust registered organization. 2. Fill Niramaya enrollment form. 3. Pay premium. 4. Card issued in 30 days.",
        "documents_required": "Disability certificate, Aadhar, BPL card if applicable, Passport photo, Bank account",
        "official_link": "https://thenationaltrust.gov.in/content/scheme/niramaya.php"
    },
    {
        "name": "UDID Card (Unique Disability Identity Card)",
        "description": "Single identity card for accessing all disability benefits across India. Replaces multiple certificates.",
        "disability_type": "all",
        "eligibility": "Any Indian citizen with 40%+ benchmark disability under RPWD Act 2016.",
        "how_to_apply": "1. Apply at swavlambancard.gov.in. 2. Visit government hospital for assessment. 3. Card issued digitally and physically.",
        "documents_required": "Aadhar, Passport photo, Medical records, Address proof, Self-declaration form",
        "official_link": "https://swavlambancard.gov.in"
    },
    {
        "name": "3% Reservation in Government Jobs",
        "description": "3% reservation in all central government posts for persons with benchmark disabilities.",
        "disability_type": "all",
        "eligibility": "40%+ benchmark disability. Must meet job-specific eligibility criteria.",
        "how_to_apply": "1. Apply through SSC/UPSC/Railway. 2. Select PwD category. 3. Produce disability certificate at document verification.",
        "documents_required": "UDID card or disability certificate (40%+), Standard job application documents",
        "official_link": "https://disabilityaffairs.gov.in"
    },
    {
        "name": "Indira Gandhi National Disability Pension",
        "description": "Monthly pension for disabled persons living below poverty line under National Social Assistance Programme.",
        "disability_type": "all",
        "eligibility": "80%+ disability. Age 18-79 years. Must have BPL card.",
        "how_to_apply": "1. Visit Gram Panchayat or Ward office. 2. Fill IGNDPS form. 3. Submit BPL and disability certificates. 4. Pension credited monthly.",
        "documents_required": "BPL card, Disability certificate (80%+), Aadhar, Age proof, Bank passbook, Residence proof",
        "official_link": "https://nsap.nic.in"
    },
]


def seed_schemes():
    db = SessionLocal()
    try:
        existing = db.query(GovernmentScheme).count()
        if existing > 0:
            print(f"⚠️  Already has {existing} schemes. Skipping.")
            return

        print("🌱 Seeding schemes...")
        for scheme in schemes_data:
            db.add(GovernmentScheme(**scheme))
        db.commit()
        print(f"✅ Seeded {len(schemes_data)} schemes successfully!")
    except Exception as e:
        db.rollback()
        print(f"❌ Failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_schemes()