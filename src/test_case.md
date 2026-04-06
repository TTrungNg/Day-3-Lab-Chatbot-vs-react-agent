###### Test cases

# 1. FAQs

Input:

- "Paracetamol dùng để làm gì?"

Expexted output:

- Mô tả công dụng thuốc
- Liều dùng cơ bản
- Cảnh báo cơ bản
- Disclaimer an toàn

Expected response:
Paracetamol là thuốc giảm đau và hạ sốt.

    Liều dùng người lớn:
    - 500mg – 1000mg mỗi 4–6 giờ
    - Không vượt quá 4000mg/ngày

    Cảnh báo:
    - Không dùng quá liều
    - Thận trọng với người bệnh gan

    Lưu ý: Tham khảo ý kiến bác sĩ trước khi sử dụng.

# 2. Tương tác thuốc nguy hiểm

Input:

- "Tôi đang dùng Warfarin và muốn dùng thêm Ibuprofen có được không?"

Expected output:

- Phát hiện tương tác nguy hiểm
- Đưa ra cảnh báo và khuyến nghị không nên dùng
- Gắn cờ cảnh báo đỏ

Expected response:
CẢNH BÁO NGUY HIỂM

Warfarin và Ibuprofen khi dùng cùng nhau có khả năng xảy ra phản ứng thuốc nguy hiểm!
Nguy cơ:

- Tăng nguy cơ chảy máu
- Xuất huyết nội

Khuyến nghị:

- Không dùng cùng nhau
- Tham khảo bác sĩ nếu muốn điều trị các triệu chứng khác

# 3. Tính liều lượng thuốc (dựa trên cân nặng, độ tuổi, trẻ em/người lớn)

Input:

- "Trẻ em 10kg nên dùng Paracetamol liều bao nhiêu?"

Expected output:

- Tính liều lượng theo cân nặng
- Hiển thị công thức tính liều lượng thuốc
- Hiển thị liều lượng khuyến nghị cho phân loại bệnh nhân (người lớn/trẻ em)

Expected response:
Liều Paracetamol cho trẻ em:
10–15 mg/kg mỗi 4–6 giờ

    Trẻ 10kg:
    -> 100mg – 150mg mỗi lần

    Khuyến cáo: không vượt quá 60mg/kg/ngày

    Lưu ý: Tham khảo bác sĩ trước khi sử dụng

# 4. Không tìm thấy dữ liệu thuốc

Input:

- "Thuốc ABC có tác dụng gì?"

Expected output:

- Trigger fallback path
- Không hallucinate
- Gợi ý user kiểm tra lại
- Cảnh báo không nên sử dụng thuốc nếu không rõ thông tin

Expected response:
Không tìm thấy thông tin thuốc "ABC" trong cơ sở dữ liệu.

    Bạn có thể:
    - Kiểm tra lại tên thuốc
    - Cung cấp tên hoạt chất
    - Cung cấp tên thương mại khác

    Lưu ý: Không nên sử dụng thuốc khi chưa xác định rõ thông tin.

# 5. Câu hỏi mơ hồ (câu hỏi dựa trên triệu chứng bệnh)

Input:

- "Tôi bị ho và đau đầu, tôi nên dùng thuốc gì?"

Expected ouput:

- Yêu cầu cung cấp thêm thông tin
- Không đưa ra thông tin thuốc cụ thể ngay (không đủ thông tin mà chỉ tư vấn dựa trên triệu chứng dễ dẫn đến các trường hợp tư vấn sai gây ra hậu quả nghiêm trọng)

Expected response:
Tôi cần thêm thông tin để tư vấn an toàn:

    - Bạn bao nhiêu tuổi?
    - Bạn có bệnh nền không?
    - Bạn đang dùng thuốc nào?

    Vui lòng cung cấp thêm thông tin.

###### Fallback logic

Flow:
User hỏi -> Tool search -> Không tìm thấy -> fallback response
Fallback response: - Không hallucinate - Gợi ý sửa lại tên - Khuyến nghị tham khảo trực tiếp dược sĩ

###### Escalation

2 trường hợp: Tool check trả về kết quả tương tác thuốc nguy hiểm (true/false)

# True case (tương tác nguy hiểm)

Expected behavior:

- Hiển thị cảnh báo
- Gắn flag ESCALATE
- Khuyến nghị tham khảo ý kiến bác sĩ trực tiếp

Expected response: Như trên test case #2

# False case (không có tương tác giữa các loại thuốc)

Expected behavior:

- Hiển thị kết quả (thông báo an toàn để sử dụng)
- Khuyến nghị đến cơ sở ý tế nếu gặp các triệu chứng bất thường sau khi sử dụng

Expected response:
Hiện không có thông tin nào về các tương tác nguy hiểm giữa Paracetamol và Warafin. Bạn có thể sử dụng an toàn.

    Lưu ý: nếu xảy ra bất kỳ triệu chứng bất thường nào sau khi sử dụng thuốc, ngay lập tức đến các cơ sở y tế để được thăm khám và điều trị kịp thời.
