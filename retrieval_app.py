import os
from tqdm.auto import tqdm
import pandas as pd
from solid_data import SolidData

class RetrievalSolidData:
    def __init__(self, directory):
        """
        Khởi tạo đối tượng với thư mục chứa các tệp dữ liệu Solid.
        - directory: Thư mục chứa dữ liệu Solid.
        """
        self.directory = directory
        self.solid_data_dict = self.load_solid_data_from_directory()

    def load_solid_data_from_directory(self):
        """
        Duyệt qua thư mục, tìm các tệp .npz và sử dụng hàm load_dok_matrix
        để tải và lưu các đối tượng SolidData vào một dictionary.
        - Trả về: Dictionary với tên dữ liệu là key và đối tượng SolidData là value.
        """
        solid_data_dict = {}
        
        # Tạo danh sách tất cả file .npz cần xử lý
        npz_files = []
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                if file.endswith(".npz"):
                    npz_files.append((root, file))
        
        # Dùng tqdm để hiển thị tiến trình
        for root, file in tqdm(npz_files, desc="Đang tải dữ liệu", unit="file"):
            file_name = os.path.splitext(file)[0]
            try:
                print(f"Đang lấy dữ liệu từ {root}")
                solid_data_dict[file_name] = SolidData.load_dok_matrix(root)
            except Exception as e:
                print(f"\nKhông thể tải dữ liệu từ {file}: {str(e)}")
        
        return solid_data_dict

    def get_data(self, lon, lat):
        """
        Duyệt qua tất cả các SolidData trong dictionary và trả về giá trị tại vị trí lon, lat.
        - lon, lat: Tọa độ lon và lat cần tra cứu.
        - Trả về: Dictionary chứa tên dữ liệu là key và giá trị tại (lon, lat) là value.
        """
        result_dict = {'name': [], 'value': []}
        for file_name, solid_data in self.solid_data_dict.items():
            try:
                name = solid_data.name
                value = solid_data[lon, lat]
                result_dict['name'].append(name)
                result_dict['value'].append(value)
            except ValueError as e:
                result_dict['name'].append(name)
                result_dict['value'].append(f"Lỗi: {e}")

        # Chuyển kết quả sang DataFrame
        df = pd.DataFrame(result_dict)
        return df

    def get_data_info(self):
        """
        Chuyển thông tin từ solid_data_dict thành DataFrame
        
        Returns:
            pd.DataFrame: DataFrame chứa các thuộc tính của các đối tượng SolidData
        """
        data = []
        
        for file_name, solid_data in self.solid_data_dict.items():
            data.append({
                'file_name': file_name,
                'name': solid_data.name,
                'rows': solid_data.rows,
                'columns': solid_data.cols,
                'x_corner': solid_data.x_corner,
                'y_corner': solid_data.y_corner,
                'cell_size': solid_data.cellsize,
                'description': getattr(solid_data, 'description', 'Unknown')  # Thêm trường description nếu có
            })
        
        # Tạo DataFrame từ danh sách dữ liệu
        df = pd.DataFrame(data)
        
        # Sắp xếp các cột (tuỳ chọn)
        columns_order = ['name', 'rows', 'columns', 'x_corner', 'y_corner', 'cell_size', 'description']
        df = df[columns_order]
        
        return df

if __name__ == "__main__":
    solid_data_path = "./solid_data"
    app = RetrievalSolidData(solid_data_path)
    
    while True:
        print("\n" + "="*50)
        print("NHẬP TỌA ĐỘ ĐỂ TRA CỨU DỮ LIỆU")
        print("="*50)
        
        try:
            # Nhập tọa độ từ người dùng
            lat = float(input("Nhập vĩ độ (latitude): "))
            lon = float(input("Nhập kinh độ (longitude): "))
            
            # Lấy dữ liệu
            df_data = app.get_data(lon, lat)
            df_data_info = app.get_data_info()
            
            # Hiển thị kết quả
            print("\nKẾT QUẢ TRA CỨU:")
            print("="*50)
            print(f"Tọa độ: Lat={lat}, Lon={lon}")
            print("\nThông tin dữ liệu:")
            print(df_data_info)
            print("\nGiá trị tại tọa độ:")
            print(df_data)
            
        except ValueError:
            print("Lỗi: Vui lòng nhập số hợp lệ cho tọa độ!")
        except KeyboardInterrupt:
            print("\nKết thúc chương trình...")
            break
        except Exception as e:
            print(f"Lỗi: {str(e)}")
        
        # Hỏi người dùng có muốn tiếp tục không
        cont = input("\nTiếp tục tra cứu? (y/n): ").lower()
        if cont != 'y':
            print("Kết thúc chương trình.")
            break