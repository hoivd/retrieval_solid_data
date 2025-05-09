import json
import os
from solid_data import SolidData

class ProcessingSolidData:
    def __init__(self, input_root="data", output_root="solid_data", data_info=None):
        """
        Khởi tạo đối tượng GenSolidData với thông tin thư mục và ánh xạ.
        - input_root: Thư mục chứa các tệp ASC (ví dụ: 'data').
        - output_root: Thư mục lưu kết quả (ví dụ: 'solid_data').
        - data_info: Dictionary chứa filename, name và dtype dữ liệu.
        """
        self.input_root = input_root
        self.output_root = output_root
        # Kiểm tra nếu data_info không được cung cấp, tạo dictionary trống
        self.data_info = data_info if data_info else {}

    def load_data_info(self, filename="data_info.json"):
        """
        Đọc file JSON và trả về dictionary ánh xạ từ filename sang name và dtype.
        - filename: Đường dẫn đến file JSON chứa bộ ánh xạ.
        """
        with open(filename, "r") as f:
            self.data_info = json.load(f)
        return self.data_info

    def process_asc_files(self):
        """
        Duyệt qua tất cả tệp .asc trong input_root, đọc và lưu vào output_root với cấu trúc tương ứng.
        """
        # Duyệt qua tất cả thư mục và tệp trong input_root
        for root, dirs, files in os.walk(self.input_root):
            for file in files:
                if file.endswith(".asc"):  # Chỉ xử lý tệp .asc
                    # Đường dẫn đầy đủ của tệp .asc
                    asc_path = os.path.join(root, file)
                    
                    # Tên tệp không có đuôi (sẽ dùng làm name và tên thư mục lưu)
                    file_name = os.path.splitext(file)[0]
                    
                    # Ánh xạ file_name sang name và dtype nếu có trong dictionary
                    data_info = self.data_info.get(file_name, {"name": file_name, "dtype": "float", "description": "Unknown"})
                    name = data_info["name"]
                    dtype = data_info["dtype"]
                    description = data_info["description"]
                    
                    # Đường dẫn tương đối từ input_root
                    relative_path = os.path.relpath(root, self.input_root)
                    if relative_path == ".":
                        output_dir = os.path.join(self.output_root, file_name)
                    else:
                        output_dir = os.path.join(self.output_root, relative_path, file_name)

                    print(f"Đang xử lý: {asc_path} -> {output_dir}")
                    
                    try:
                        # Đọc tệp .asc và tạo SolidData với name từ ánh xạ
                        data = SolidData.read_asc(asc_path, name=name, dtype=dtype, description=description)
                        
                        try:
                            data.plot(os.path.join(output_dir, "heatmap.png"))
                        except Exception as e:
                            print(f"Lỗi khi xử lý {asc_path}: {str(e)}")

                        # Lưu ma trận và metadata vào output_dir
                        data.save_dok_matrix(output_dir)
                        
                        print(f"Đã lưu thành công: {output_dir}")
                    except Exception as e:
                        print(f"Lỗi khi xử lý {asc_path}: {str(e)}")
                        
    
    def generate_data_info_json(self, output_file="data_info.json"):
        """
        Tạo file JSON ánh xạ filename sang name và dtype cho tất cả các tệp .asc trong thư mục input_root.
        - output_file: Đường dẫn đến file JSON sẽ được tạo.
        """
        data_info = {}

        # Duyệt qua tất cả tệp .asc trong input_root
        for root, dirs, files in os.walk(self.input_root):
            for file in files:
                if file.endswith(".asc"):  # Chỉ xử lý tệp .asc
                    file_name = os.path.splitext(file)[0]
                    # Mặc định name và dtype
                    name = file_name  # Dùng file_name làm name mặc định
                    dtype = "float"  # Kiểu dữ liệu mặc định

                    # Thêm vào dictionary
                    data_info[file_name] = {"name": name, "dtype": dtype, "description": "Unknown"}

        # Lưu dictionary vào file JSON
        with open(output_file, "w") as f:
            json.dump(data_info, f, indent=4)
        
        print(f"File JSON đã được tạo: {output_file}")


if __name__ == "__main__":
    # Khởi tạo đối tượng GenSolidData
    input_dir = "./data"
    output_dir = "./solid_data"
    
    gen_solid_data = ProcessingSolidData(input_root=input_dir, output_root=output_dir)
    
    # Tạo file JSON chứa ánh xạ từ filename sang name và dtype
    # gen_solid_data.generate_data_info_json("data_info.json")
    
    # Đọc bộ ánh xạ từ file JSON
    gen_solid_data.load_data_info("data_info.json")
    
    # Gọi phương thức để xử lý các tệp ASC
    gen_solid_data.process_asc_files()
