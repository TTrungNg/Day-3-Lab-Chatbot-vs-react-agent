============================ Chatbot & Agent Compilation ============================
# Test case #1
#                   |Chatbot                                |Agent                                       |
Test case 1         |Trả lời dựa trên kiến thức sẵn         |Gọi tool tra cứu tên thuốc, chạy agent loop,|
                    |có, latency thấp                       |latency tệ hơn                              |
---------------------------------------------------------------------------------------------------------|                  
Test case 2         |Trả lời mơ hồ về tình trang tương tác  |Cung cấp thông tin đầy đủ, chính xác, bao   |
                    |của 2 loại thuốc, dễ gây hiểu nhầm     |gồm cả triệu chứng nếu mắc phải và gắn cờ   |
                    |                                       |cảnh báo đỏ                                 |
---------------------------------------------------------------------------------------------------------|                  
Test case 3         |Không thể tính toán liều lượng thuốc   |Gọi tool tính toán liều lượng, cung cấp và  |
                    |chính xác dựa trên cân nặng hoặc độ    |hiển thị liều lượng khuyến nghị và công thức|
                    |tuổi                                   |tính liều lượng                             |
---------------------------------------------------------------------------------------------------------|
Test case 4         |Trong trường hợp các loại thuốc mới    |Trigger fallback path, gợi ý người dùng kiểm|
                    |mới phát hành và chưa có trong dữ liệu |tra lại tên thuốc, không bịa đặt thông tin  |
                    |sẵn, chatbot sẽ hallucinate và bịa ra  |gây nhầm lẫn                                |
                    |thông tin thuốc                        |                                            |
---------------------------------------------------------------------------------------------------------|
Test case 5         |Bị fall sang trường hợp không có thông |Yêu cầu người dùng cung cấp thêm thông tin  |
                    |tin liên quan (test case 6)            |để tư vấn chính xác, không cố gắng tư vấn   |
                    |                                       |dựa trên thông tin còn thiếu                |
---------------------------------------------------------------------------------------------------------|
Test case 6         |Nhận diện được câu hỏi không liên quan |Nhận diện được câu hỏi không liên quan      |
                    |điều hướng về phạm vi hệ thống và không|điều hướng về phạm vi hệ thống và không     |
                    |cung cấp thông tin ngoài lề            |cung cấp thông tin ngoài lề                 |