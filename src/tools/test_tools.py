import unittest

from tools import search_drug, check_interaction, calculate_dose


class TestTools(unittest.TestCase):
    def test_search_drug_found(self):
        result = search_drug("Ibuprofen")
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Ibuprofen")

    def test_search_drug_case_insensitive(self):
        result = search_drug("parAcetamol")
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Paracetamol")

    def test_search_drug_not_found(self):
        self.assertIsNone(search_drug("UnknownDrug"))

    def test_check_interaction_dangerous(self):
        result = check_interaction("Warfarin", "Ibuprofen")
        self.assertEqual(result["interaction"], "dangerous")
        self.assertIn("chảy máu", result["message"].lower())

    def test_check_interaction_same_drug(self):
        result = check_interaction("Aspirin", "Aspirin")
        self.assertEqual(result["interaction"], "same drug")
        self.assertEqual(result["drug1"], "Aspirin")
        self.assertEqual(result["drug2"], "Aspirin")

    def test_check_interaction_low(self):
        result = check_interaction("Aspirin", "Omeprazole")
        self.assertEqual(result["interaction"], "low")
        self.assertEqual(result["category1"], "Thuốc giảm đau")
        self.assertEqual(result["category2"], "Ức chế bơm proton")

    def test_search_drug_localized_entry(self):
        result = search_drug("Alyftrek")
        self.assertIsNotNone(result)
        self.assertEqual(result["tên"], "Alyftrek")
        self.assertEqual(result["liều_dùng_người_lớn"].startswith("2 viên"), True)

    def test_check_interaction_unknown(self):
        result = check_interaction("Aspirin", "UnknownDrug")
        self.assertEqual(result["interaction"], "unknown")

    def test_calculate_dose_child_weight_based(self):
        result = calculate_dose("Ibuprofen", weight_kg=20, age_years=10)
        self.assertEqual(result["age_group"], "child")
        self.assertEqual(result["recommended_dose"], "5-10mg/kg mỗi 6-8 giờ")
        self.assertEqual(result["calculated_dose"], "100-200mg mỗi 6-8 giờ")

    def test_calculate_dose_adult_standard(self):
        result = calculate_dose("Omeprazole", weight_kg=70, age_years=30)
        self.assertEqual(result["age_group"], "adult")
        self.assertEqual(result["recommended_dose"], "20mg mỗi ngày một lần")
        self.assertEqual(result["calculated_dose"], "20mg mỗi ngày một lần")
        self.assertIn("note", result)

    def test_calculate_dose_invalid_weight(self):
        result = calculate_dose("Aspirin", weight_kg=0, age_years=25)
        self.assertEqual(result["error"], "Invalid weight. Weight must be a positive number.")

    def test_calculate_dose_invalid_age(self):
        result = calculate_dose("Aspirin", weight_kg=70, age_years=-1)
        self.assertEqual(result["error"], "Invalid age. Age must be a non-negative number.")

    def test_calculate_dose_unknown_drug(self):
        self.assertIsNone(calculate_dose("UnknownDrug", weight_kg=30, age_years=10))


if __name__ == "__main__":
    unittest.main()
