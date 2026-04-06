# Mock database medicine

medicines = {
    "Aspirin": {
        "name": "Aspirin",
        "dose_adults": "325-650mg mỗi 4-6 giờ",
        "dose_children": "Không khuyến cáo cho trẻ dưới 16 tuổi",
        "category": "Thuốc giảm đau",
        "contraindications": "Dị ứng aspirin, rối loạn chảy máu, loét dạ dày",
        "main_active_ingredient": "Acid acetylsalicylic"
    },
    "Ibuprofen": {
        "name": "Ibuprofen",
        "dose_adults": "200-400mg mỗi 4-6 giờ",
        "dose_children": "5-10mg/kg mỗi 6-8 giờ",
        "category": "Thuốc chống viêm không steroid (NSAID)",
        "contraindications": "Dị ứng NSAIDs, loét dạ dày, bệnh thận",
        "main_active_ingredient": "Ibuprofen"
    },
    "Paracetamol": {
        "name": "Paracetamol",
        "dose_adults": "500-1000mg mỗi 4-6 giờ",
        "dose_children": "10-15mg/kg mỗi 4-6 giờ",
        "category": "Thuốc giảm đau",
        "contraindications": "Bệnh gan, dị ứng paracetamol",
        "main_active_ingredient": "Paracetamol"
    },
    "Amoxicillin": {
        "name": "Amoxicillin",
        "dose_adults": "500mg mỗi 8 giờ",
        "dose_children": "20-40mg/kg/ngày chia 3 lần",
        "category": "Kháng sinh",
        "contraindications": "Dị ứng penicillin",
        "main_active_ingredient": "Amoxicillin"
    },
    "Omeprazole": {
        "name": "Omeprazole",
        "dose_adults": "20mg mỗi ngày một lần",
        "dose_children": "0,7-1,4mg/kg mỗi ngày một lần",
        "category": "Ức chế bơm proton",
        "contraindications": "Dị ứng omeprazole",
        "main_active_ingredient": "Omeprazole"
    },
    "Simvastatin": {
        "name": "Simvastatin",
        "dose_adults": "10-40mg mỗi ngày một lần",
        "dose_children": "Không dùng thường xuyên cho trẻ em",
        "category": "Statin",
        "contraindications": "Bệnh gan, mang thai",
        "main_active_ingredient": "Simvastatin"
    },
    "Metformin": {
        "name": "Metformin",
        "dose_adults": "500-1000mg hai lần mỗi ngày",
        "dose_children": "500mg hai lần mỗi ngày cho tiểu đường type 2",
        "category": "Thuốc điều trị đái tháo đường",
        "contraindications": "Bệnh thận, nhiễm toan lactic",
        "main_active_ingredient": "Metformin"
    },
    "Lisinopril": {
        "name": "Lisinopril",
        "dose_adults": "10-40mg mỗi ngày một lần",
        "dose_children": "0,07mg/kg mỗi ngày một lần",
        "category": "Ức chế ACE",
        "contraindications": "Mang thai, tăng kali huyết",
        "main_active_ingredient": "Lisinopril"
    },
    "Amlodipine": {
        "name": "Amlodipine",
        "dose_adults": "5-10mg mỗi ngày một lần",
        "dose_children": "0,1-0,2mg/kg mỗi ngày một lần",
        "category": "Chẹn kênh canxi",
        "contraindications": "Huyết áp thấp, suy tim",
        "main_active_ingredient": "Amlodipine"
    },
    "Warfarin": {
        "name": "Warfarin",
        "dose_adults": "2-10mg mỗi ngày một lần (điều chỉnh theo INR)",
        "dose_children": "0,1-0,2mg/kg mỗi ngày một lần",
        "category": "Thuốc chống đông máu",
        "contraindications": "Rối loạn đông máu, mang thai",
        "main_active_ingredient": "Warfarin"
    },
    "Prednisone": {
        "name": "Prednisone",
        "dose_adults": "5-60mg mỗi ngày (tùy theo bệnh)",
        "dose_children": "0,5-2mg/kg mỗi ngày",
        "category": "Corticosteroid",
        "contraindications": "Nhiễm trùng, tiểu đường",
        "main_active_ingredient": "Prednisone"
    },
    "Furosemide": {
        "name": "Furosemide",
        "dose_adults": "20-80mg mỗi ngày một hoặc hai lần",
        "dose_children": "1-2mg/kg hai lần mỗi ngày",
        "category": "Thuốc lợi tiểu",
        "contraindications": "Suy thận, mất cân bằng điện giải",
        "main_active_ingredient": "Furosemide"
    },
    "Alyftrek": {
        "tên": "Alyftrek",
        "liều_dùng_người_lớn": "2 viên (vanzacaftor 200mg/tezacaftor 150mg/deutivacaftor 200mg) uống một lần mỗi ngày vào buổi sáng",
        "liều_dùng_trẻ_em": "Dành cho trẻ từ 6 tuổi trở lên, liều lượng điều chỉnh theo cân nặng (thường là 1 viên/ngày cho trẻ dưới 30kg)",
        "loại_thuốc": "Thuốc điều hòa protein CFTR (Cystic Fibrosis Transmembrane Conductance Regulator)",
        "chống_chỉ_ định": "Quá mẫn với bất kỳ thành phần nào của thuốc, suy gan nặng",
        "thành_phần_chính": "Vanzacaftor, Tezacaftor, Deutivacaftor"
    },
    "Datroway": {
        "tên": "Datroway",
        "liều_dùng_người_lớn": "6.0 mg/kg truyền tĩnh mạch mỗi 3 tuần một lần",
        "liều_dùng_trẻ_em": "Chưa được xác định an toàn và hiệu quả cho trẻ em",
        "loại_thuốc": "Kháng thể liên hợp kháng TROP2 (ADC)",
        "chống_chỉ_ định": "Phụ nữ mang thai, người có bệnh phổi kẽ (ILD) tiến triển",
        "thành_phần_chính": "Datopotamab deruxtecan"
    },
    "Journavx": {
        "tên": "Journavx",
        "liều_dùng_người_lớn": "70 mg uống một lần duy nhất, sau đó 35 mg mỗi 12 giờ",
        "liều_dùng_trẻ_em": "Chưa có chỉ định cho trẻ em dưới 18 tuổi",
        "loại_thuốc": "Thuốc ức chế kênh Natri NaV1.8 (Giảm đau không opioid)",
        "chống_chỉ_ định": "Suy thận nặng, mẫn cảm với Suzetrigine",
        "thành_phần_chính": "Suzetrigine"
    },
    "Aficamten": {
        "tên": "Aficamten",
        "liều_dùng_người_lớn": "Bắt đầu với 5 mg/ngày, có thể tăng dần lên tối đa 15 mg/ngày dựa trên kết quả siêu âm tim",
        "liều_dùng_trẻ_em": "Chưa có dữ liệu lâm sàng cho trẻ em",
        "loại_thuốc": "Thuốc ức chế myosin tim thế hệ mới",
        "chống_chỉ_ định": "Phân suất tống máu thất trái (LVEF) < 50%",
        "thành_phần_chính": "Aficamten"
    },
    "Brensocatib": {
        "tên": "Brensocatib",
        "liều_dùng_người_lớn": "10 mg hoặc 25 mg uống một lần mỗi ngày",
        "liều_dùng_trẻ_em": "Chưa được phê duyệt sử dụng cho trẻ em",
        "loại_thuốc": "Thuốc ức chế Dipeptidyl peptidase 1 (DPP1)",
        "chống_chỉ_ định": "Mẫn cảm với thành phần thuốc, bệnh gan tiến triển",
        "thành_phần_chính": "Brensocatib"
    },
    "Tolebrutinib": {
        "tên": "Tolebrutinib",
        "liều_dùng_người_lớn": "60 mg uống một lần mỗi ngày",
        "liều_dùng_trẻ_em": "Chưa được nghiên cứu ở trẻ em",
        "loại_thuốc": "Thuốc ức chế Bruton's tyrosine kinase (BTK) xuyên hàng rào máu não",
        "chống_chỉ_ định": "Nhiễm trùng cấp tính nặng, suy gan nặng",
        "thành_phần_chính": "Tolebrutinib"
    },
    "Mazdutide": {
        "tên": "Mazdutide",
        "liều_dùng_người_lớn": "Tiêm dưới da một lần mỗi tuần, liều duy trì thường là 4.5 mg hoặc 6 mg",
        "liều_dùng_trẻ_em": "Chưa có chỉ định cho trẻ em",
        "loại_thuốc": "Chất chủ vận kép thụ thể GLP-1 và Glucagon",
        "chống_chỉ_ định": "Tiền sử cá nhân hoặc gia đình bị ung thư biểu mô tuyến giáp dạng tủy",
        "thành_phần_chính": "Mazdutide"
    },
    "Depemokimab": {
        "tên": "Depemokimab",
        "liều_dùng_người_lớn": "100 mg tiêm dưới da mỗi 6 tháng một lần",
        "liều_dùng_trẻ_em": "Đang trong giai đoạn thử nghiệm cho trẻ vị thành niên",
        "loại_thuốc": "Kháng thể đơn dòng kháng IL-5 tác dụng kéo dài",
        "chống_chỉ_ định": "Mẫn cảm với thành phần thuốc, nhiễm ký sinh trùng chưa điều trị",
        "thành_phần_chính": "Depemokimab"
    },
    "MenABCWY vaccine": {
        "tên": "MenABCWY vaccine",
        "liều_dùng_người_lớn": "Tiêm bắp 2 liều cách nhau 6-12 tháng",
        "liều_dùng_trẻ_em": "Được chỉ định cho thanh thiếu niên từ 10-25 tuổi",
        "loại_thuốc": "Vắc-xin cộng hợp não mô cầu nhóm A, B, C, W, Y",
        "chống_chỉ_ định": "Phản ứng dị ứng nghiêm trọng sau liều tiêm vắc-xin não mô cầu trước đó",
        "thành_phần_chính": "Kháng nguyên từ vắc-xin Menveo và Bexsero"
    },
    "Nipocalimab": {
        "tên": "Nipocalimab",
        "liều_dùng_người_lớn": "30 mg/kg truyền tĩnh mạch mỗi 2 tuần",
        "liều_dùng_trẻ_em": "Chưa có liều lượng tiêu chuẩn, đang thử nghiệm cho trẻ bị nhược cơ khởi phát sớm",
        "loại_thuốc": "Kháng thể đơn dòng kháng thụ thể Fc sơ sinh (FcRn)",
        "chống_chỉ_ định": "Nhiễm trùng nặng hoạt động, mẫn cảm với thành phần thuốc",
        "thành_phần_chính": "Nipocalimab"
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


def _get_med_field(med, *keys):
    for key in keys:
        if key in med:
            return med[key]
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
            "message": "Một trong 2 loại thuốc không được tìm thấy trong cơ sở dữ liệu mô phỏng."
        }

    med1_name = _get_med_field(med1, "name", "tên")
    med2_name = _get_med_field(med2, "name", "tên")
    if med1_name == med2_name:
        return {
            "drug1": med1_name,
            "drug2": med2_name,
            "interaction": "same drug",
            "message": "Cùng một loại thuốc đã được cung cấp hai lần."
        }

    category1 = _get_med_field(med1, "category", "loại_thuốc") or "Unknown"
    category2 = _get_med_field(med2, "category", "loại_thuốc") or "Unknown"
    pair = frozenset([category1, category2])

    interaction_rules = {
        frozenset({"Thuốc chống đông máu", "Corticosteroid"}): (
            "dangerous",
            "Nguy cơ chảy máu tăng cao khi thuốc chống đông được kết hợp với corticosteroid."
        ),
        frozenset({"Thuốc chống đông máu", "Thuốc chống viêm không steroid (NSAID)"}): (
            "dangerous",
            "NSAID có thể làm tăng nguy cơ chảy máu khi dùng cùng với thuốc chống đông."
        ),
        frozenset({"Thuốc chống đông máu", "Kháng sinh"}): (
            "moderate",
            "Một số kháng sinh có thể thay đổi nồng độ thuốc chống đông; cần theo dõi."
        ),
        frozenset({"Thuốc chống đông máu", "Statin"}): (
            "moderate",
            "Một số statin có thể thay đổi nồng độ thuốc chống đông; cần thận trọng."
        ),
        frozenset({"Chẹn kênh canxi", "Ức chế ACE"}): (
            "moderate",
            "Kết hợp hai thuốc này có thể làm hạ huyết áp và cần được theo dõi."
        ),
        frozenset({"Chẹn kênh canxi", "Thuốc lợi tiểu"}): (
            "moderate",
            "Có thể tăng hiệu quả hạ huyết áp và thay đổi điện giải."
        ),
        frozenset({"Thuốc lợi tiểu", "Ức chế ACE"}): (
            "moderate",
            "Kết hợp ức chế ACE và lợi tiểu có thể hạ huyết áp và cần theo dõi chức năng thận."
        ),
        frozenset({"Thuốc lợi tiểu", "Thuốc chống viêm không steroid (NSAID)"}): (
            "moderate",
            "NSAID có thể làm giảm hiệu quả của thuốc lợi tiểu và ảnh hưởng tới chức năng thận."
        ),
        frozenset({"Ức chế ACE", "Thuốc chống viêm không steroid (NSAID)"}): (
            "moderate",
            "NSAID có thể giảm hiệu quả của ức chế ACE và ảnh hưởng tới chức năng thận."
        ),
        frozenset({"Thuốc giảm đau", "Thuốc chống viêm không steroid (NSAID)"}): (
            "caution",
            "Dùng đồng thời thuốc giảm đau và NSAID có thể tăng tác dụng phụ và cần thận trọng."
        ),
        frozenset({"Thuốc giảm đau", "Thuốc giảm đau"}): (
            "caution",
            "Dùng hai thuốc giảm đau cùng nhau có thể tăng tác dụng phụ và cần được theo dõi."
        ),
        frozenset({"Thuốc lợi tiểu", "Thuốc lợi tiểu"}): (
            "caution",
            "Dùng hai thuốc lợi tiểu cùng nhau có thể tăng nguy cơ mất nước và rối loạn điện giải."
        ),
        frozenset({"Corticosteroid", "Thuốc lợi tiểu"}): (
            "caution",
            "Có thể tăng nguy cơ rối loạn điện giải và thay đổi huyết áp."
        )
    }

    interaction = interaction_rules.get(pair)
    if interaction:
        level, message = interaction
        return {
            "drug1": med1_name,
            "drug2": med2_name,
            "interaction": level,
            "message": message,
            "category1": category1,
            "category2": category2
        }

    if category1 == category2:
        return {
            "drug1": med1_name,
            "drug2": med2_name,
            "interaction": "caution",
            "message": f"Cả hai thuốc đều thuộc loại ({category1}), có thể tăng tác dụng cộng gộp.",
            "category1": category1,
            "category2": category2
        }

    return {
        "drug1": med1_name,
        "drug2": med2_name,
        "interaction": "low",
        "message": "Không tìm thấy tương tác nghiêm trọng dựa trên danh mục.",
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
        dose_text = _get_med_field(med, "dose_children", "liều_dùng_trẻ_em")
        age_group = "child"
    else:
        dose_text = _get_med_field(med, "dose_adults", "liều_dùng_người_lớn")
        age_group = "adult"

    if dose_text is None:
        return {
            "drug": _get_med_field(med, "name", "tên"),
            "error": "Dose information not available for this medicine."
        }

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
