# Xử Lý Dữ Liệu Raster

## Mô tả

Chương trình này cho phép bạn truy vấn và xử lý dữ liệu từ các tệp raster. Các tệp raster được chuyển thành ma trận sparse DOK (Dictionary Of Keys) để tối ưu bộ nhớ và hiệu suất trong việc truy xuất và xử lý. Mô hình dữ liệu giúp lưu trữ và truy xuất thông tin địa lý dựa trên tọa độ (kinh độ, vĩ độ).

## Các tệp trong dự án

- **prepare_solid_data.py**: Chứa mã để chuyển đổi dữ liệu raster thành `dok_matrix` (ma trận sparse).
- **solid_data.py**: Định nghĩa cấu trúc dữ liệu và các hàm xử lý dữ liệu.
- **retrieval_app.py**: Chứa các chức năng truy vấn dữ liệu, bao gồm hàm `get_data()` để truy xuất dữ liệu từ tọa độ.
- **data_info.json**: Tệp chứa thông tin chi tiết về từng file raster.

## Cách sử dụng

### Cài đặt môi trường

1. Cài đặt các thư viện yêu cầu:
    ```bash
    pip install -r requirements.txt
    ```

2. Tạo môi trường ảo (khuyến khích):
    ```bash
    python -m venv myenv
    myenv\Scripts\activate     # Trên Windows
    ```

### Chạy ứng dụng

1. Để truy vấn dữ liệu, bạn cần chạy `retrieval_app.py` và nhập vào các tọa độ kinh độ và vĩ độ. Sau đó, bạn có thể truy xuất dữ liệu từ file raster.

    ```bash
    python retrieval_app.py
    ```

2. Trong ứng dụng, bạn có thể sử dụng hàm `get_data(lon, lat)` để lấy dữ liệu từ vị trí mà bạn cung cấp. Lưu ý rằng bạn cần phải khởi tạo một đối tượng của lớp `RetrievalSolidData` trước khi gọi phương thức `get_data()`.

    ```python
    from retrieval_app import RetrievalSolidData
    
    # Khởi tạo đối tượng RetrievalSolidData
    retrieval_data = RetrievalSolidData()

    # Nhập tọa độ kinh độ và vĩ độ
    lon = 105.8542  # Kinh độ
    lat = 21.0285   # Vĩ độ

    # Gọi phương thức get_data để lấy dữ liệu
    data = retrieval_data.get_data(lon, lat)

    # In dữ liệu lấy được
    print(data)
    ```

3. Hàm `get_data_info()` sẽ cung cấp thông tin chi tiết về các cột dữ liệu trong file raster.

    ```python
    from retrieval_app import RetrievalSolidData
    
    # Khởi tạo đối tượng RetrievalSolidData
    retrieval_data = RetrievalSolidData()

    # Lấy thông tin cột dữ liệu
    info = get_data_info()
    print(info)
    ```

## Giới thiệu các hàm

### `get_data(lon, lat)`

- **Mô tả**: Truy vấn dữ liệu raster tại vị trí tọa độ (lon, lat).
- **Tham số**: 
  - `lon` (float): Kinh độ.
  - `lat` (float): Vĩ độ.
- **Trả về**: Dữ liệu tại tọa độ được cung cấp.

### `get_data_info()`

- **Mô tả**: Trả về thông tin chi tiết về các cột trong dữ liệu raster.
- **Trả về**: Một từ điển chứa thông tin chi tiết của các cột.
