# Mock database medicine

medicines = {
    "Aspirin": {
        "name": "Aspirin",
        "dose_adults": "325-650mg every 4-6 hours",
        "dose_children": "Not recommended for children under 16",
        "category": "Analgesic",
        "contraindications": "Allergy to aspirin, bleeding disorders, ulcers",
        "main_active_ingredient": "Acetylsalicylic acid"
    },
    "Ibuprofen": {
        "name": "Ibuprofen",
        "dose_adults": "200-400mg every 4-6 hours",
        "dose_children": "5-10mg/kg every 6-8 hours",
        "category": "Non-steroidal anti-inflammatory drug (NSAID)",
        "contraindications": "Allergy to NSAIDs, stomach ulcers, kidney disease",
        "main_active_ingredient": "Ibuprofen"
    },
    "Paracetamol": {
        "name": "Paracetamol",
        "dose_adults": "500-1000mg every 4-6 hours",
        "dose_children": "10-15mg/kg every 4-6 hours",
        "category": "Analgesic",
        "contraindications": "Liver disease, allergy to paracetamol",
        "main_active_ingredient": "Paracetamol"
    },
    "Amoxicillin": {
        "name": "Amoxicillin",
        "dose_adults": "500mg every 8 hours",
        "dose_children": "20-40mg/kg/day divided into 3 doses",
        "category": "Antibiotic",
        "contraindications": "Allergy to penicillin",
        "main_active_ingredient": "Amoxicillin"
    },
    "Omeprazole": {
        "name": "Omeprazole",
        "dose_adults": "20mg once daily",
        "dose_children": "0.7-1.4mg/kg once daily",
        "category": "Proton pump inhibitor",
        "contraindications": "Allergy to omeprazole",
        "main_active_ingredient": "Omeprazole"
    },
    "Simvastatin": {
        "name": "Simvastatin",
        "dose_adults": "10-40mg once daily",
        "dose_children": "Not typically used in children",
        "category": "Statin",
        "contraindications": "Liver disease, pregnancy",
        "main_active_ingredient": "Simvastatin"
    },
    "Metformin": {
        "name": "Metformin",
        "dose_adults": "500-1000mg twice daily",
        "dose_children": "500mg twice daily for type 2 diabetes",
        "category": "Antidiabetic",
        "contraindications": "Kidney disease, lactic acidosis",
        "main_active_ingredient": "Metformin"
    },
    "Lisinopril": {
        "name": "Lisinopril",
        "dose_adults": "10-40mg once daily",
        "dose_children": "0.07mg/kg once daily",
        "category": "ACE inhibitor",
        "contraindications": "Pregnancy, hyperkalemia",
        "main_active_ingredient": "Lisinopril"
    },
    "Amlodipine": {
        "name": "Amlodipine",
        "dose_adults": "5-10mg once daily",
        "dose_children": "0.1-0.2mg/kg once daily",
        "category": "Calcium channel blocker",
        "contraindications": "Low blood pressure, heart failure",
        "main_active_ingredient": "Amlodipine"
    },
    "Warfarin": {
        "name": "Warfarin",
        "dose_adults": "2-10mg once daily (adjusted by INR)",
        "dose_children": "0.1-0.2mg/kg once daily",
        "category": "Anticoagulant",
        "contraindications": "Bleeding disorders, pregnancy",
        "main_active_ingredient": "Warfarin"
    },
    "Prednisone": {
        "name": "Prednisone",
        "dose_adults": "5-60mg daily (depending on condition)",
        "dose_children": "0.5-2mg/kg daily",
        "category": "Corticosteroid",
        "contraindications": "Infections, diabetes",
        "main_active_ingredient": "Prednisone"
    },
    "Furosemide": {
        "name": "Furosemide",
        "dose_adults": "20-80mg once or twice daily",
        "dose_children": "1-2mg/kg twice daily",
        "category": "Diuretic",
        "contraindications": "Kidney failure, electrolyte imbalance",
        "main_active_ingredient": "Furosemide"
    }
}


def search_drug(drug_name):
    """Look up a drug by name in the mock database."""
    if not isinstance(drug_name, str):
        return None

    normalized = drug_name.strip().lower()
    for name, data in medicines.items():
        if name.lower() == normalized:
            return data

    return None


def check_interaction(drug1, drug2):
    """Check whether two medicines may interact based on their categories."""
    med1 = search_drug(drug1)
    med2 = search_drug(drug2)

    if med1 is None or med2 is None:
        return {
            "drug1": drug1,
            "drug2": drug2,
            "interaction": "unknown",
            "message": "One or both drugs were not found in the mock database."
        }

    if med1["name"] == med2["name"]:
        return {
            "drug1": med1["name"],
            "drug2": med2["name"],
            "interaction": "same drug",
            "message": "The same drug was provided twice."
        }

    category1 = med1["category"]
    category2 = med2["category"]
    pair = tuple(sorted([category1, category2]))

    interaction_rules = {
        ("Anticoagulant", "Corticosteroid"): (
            "dangerous",
            "Increased bleeding risk when anticoagulants are combined with corticosteroids."
        ),
        ("Anticoagulant", "Non-steroidal anti-inflammatory drug (NSAID)" ): (
            "dangerous",
            "NSAIDs can increase the risk of bleeding when taken with anticoagulants."
        ),
        ("Anticoagulant", "Statin"): (
            "moderate",
            "Some statins may alter anticoagulant levels; use with caution."
        ),
        ("Calcium channel blocker", "ACE inhibitor"): (
            "moderate",
            "Combination can lower blood pressure and should be monitored."
        ),
        ("Calcium channel blocker", "Diuretic"): (
            "moderate",
            "May increase blood pressure lowering effects and electrolyte changes."
        ),
        ("Diuretic", "Non-steroidal anti-inflammatory drug (NSAID)"): (
            "moderate",
            "NSAIDs can reduce diuretic effectiveness and affect kidney function."
        ),
        ("ACE inhibitor", "Non-steroidal anti-inflammatory drug (NSAID)"): (
            "moderate",
            "NSAIDs may reduce the effectiveness of ACE inhibitors and affect kidney function."
        ),
        ("Analgesic", "Analgesic"): (
            "caution",
            "Using two analgesics together may increase side effects and should be monitored."
        ),
        ("Diuretic", "Diuretic"): (
            "caution",
            "Two diuretics together can increase dehydration and electrolyte imbalance risk."
        ),
        ("Corticosteroid", "Diuretic"): (
            "caution",
            "May increase the risk of electrolyte imbalance and blood pressure changes."
        )
    }

    interaction = interaction_rules.get(pair)
    if interaction:
        level, message = interaction
        return {
            "drug1": med1["name"],
            "drug2": med2["name"],
            "interaction": level,
            "message": message,
            "category1": category1,
            "category2": category2
        }

    if category1 == category2:
        return {
            "drug1": med1["name"],
            "drug2": med2["name"],
            "interaction": "caution",
            "message": f"Both drugs are in the same category ({category1}), which may increase additive effects.",
            "category1": category1,
            "category2": category2
        }

    return {
        "drug1": med1["name"],
        "drug2": med2["name"],
        "interaction": "low",
        "message": "No major interaction found based on category.",
        "category1": category1,
        "category2": category2
    }


def _calculate_mgkg_dose(dose_text, weight_kg):
    import re

    pattern = r"(\d+(?:\.\d+)?)(?:-(\d+(?:\.\d+)?))?mg/kg"
    match = re.search(pattern, dose_text)
    if not match:
        return None

    low = float(match.group(1))
    high = float(match.group(2)) if match.group(2) else low
    low_mg = low * weight_kg
    high_mg = high * weight_kg

    def format_mg(value):
        if value.is_integer():
            return str(int(value))
        return f"{value:.2f}"

    if high != low:
        replacement = f"{format_mg(low_mg)}-{format_mg(high_mg)}mg"
    else:
        replacement = f"{format_mg(low_mg)}mg"

    return re.sub(pattern, replacement, dose_text, count=1)


def calculate_dose(drug_name, weight_kg, age_years):
    """Calculate a dose based on user weight and age."""
    med = search_drug(drug_name)
    if med is None:
        return None

    if not isinstance(weight_kg, (int, float)) or weight_kg <= 0:
        return {
            "drug": drug_name,
            "error": "Invalid weight. Weight must be a positive number."
        }

    if not isinstance(age_years, (int, float)) or age_years < 0:
        return {
            "drug": drug_name,
            "error": "Invalid age. Age must be a non-negative number."
        }

    if age_years < 16:
        dose_text = med["dose_children"]
        age_group = "child"
    else:
        dose_text = med["dose_adults"]
        age_group = "adult"

    if "mg/kg" in dose_text.lower():
        calculated = _calculate_mgkg_dose(dose_text, weight_kg)
        return {
            "drug": med["name"],
            "age_group": age_group,
            "weight_kg": weight_kg,
            "recommended_dose": dose_text,
            "calculated_dose": calculated
        }

    return {
        "drug": med["name"],
        "age_group": age_group,
        "weight_kg": weight_kg,
        "recommended_dose": dose_text,
        "calculated_dose": dose_text,
        "note": "Dose is not weight-based; standard dose is returned."
    }
