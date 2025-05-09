import numpy as np
from scipy.sparse import dok_matrix, save_npz, load_npz
from tqdm.auto import tqdm
import json
import os

class LonLatMapper:
    def __init__(self, x_corner, y_corner, cellsize, rows, cols):
        """
        Khởi tạo bộ ánh xạ lon-lat sang x-y và ngược lại.
        - x_corner: Tọa độ x (kinh độ) của góc dưới-trái ô đầu tiên.
        - y_corner: Tọa độ y (vĩ độ) của góc dưới-trái ô đầu tiên.
        - cellsize: Kích thước ô lưới (độ hoặc mét).
        - rows: Số hàng của lưới.
        - cols: Số cột của lưới.
        """
        self.x_corner = x_corner
        self.y_corner = y_corner
        self.cellsize = cellsize
        self.rows = rows
        self.cols = cols
    
    def lonlat2xy(self, lon, lat):
        """
        Ánh xạ (lon, lat) sang chỉ số ô lưới (x, y).
        - lon: Kinh độ (hoặc tọa độ x trong hệ chiếu).
        - lat: Vĩ độ (hoặc tọa độ y trong hệ chiếu).
        - Trả về: (x, y) - chỉ số cột và hàng.
        """
        x = int(round((lon - self.x_corner) / self.cellsize))
        y = abs(int(round((lat + self.y_corner) / self.cellsize)))
        
        # Kiểm tra giới hạn
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            raise ValueError(f"Chỉ số (x={x}, y={y}) ngoài phạm vi lưới ({self.cols}x{self.rows})")
        
        return x, y
    
    def xy2lonlat(self, x, y):
        """
        Ánh xạ chỉ số ô lưới (x, y) sang (lon, lat).
        - x: Chỉ số cột.
        - y: Chỉ số hàng.
        - Trả về: (lon, lat) - kinh độ và vĩ độ.
        """
        # Kiểm tra giới hạn
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            raise ValueError(f"Chỉ số (x={x}, y={y}) ngoài phạm vi lưới ({self.cols}x{self.rows})")
        
        lon = self.x_corner + x * self.cellsize
        lat = abs(self.y_corner) - y * self.cellsize
        return lon, lat
    
    def lonlat2xy_batch(self, lons, lats):
        """
        Ánh xạ hàng loạt (lon, lat) sang (x, y).
        - lons, lats: Mảng hoặc danh sách kinh độ và vĩ độ.
        - Trả về: Danh sách (x, y).
        """
        lons = np.asarray(lons)
        lats = np.asarray(lats)
        x = np.round((lons - self.x_corner) / self.cellsize).astype(int)
        y = np.abs(np.round((lats + self.y_corner) / self.cellsize)).astype(int)
        
        # Kiểm tra giới hạn
        valid = (x >= 0) & (x < self.cols) & (y >= 0) & (y < self.rows)
        if not valid.all():
            raise ValueError("Một số tọa độ ngoài phạm vi lưới")
        
        return list(zip(x, y))
    
    def xy2lonlat_batch(self, xs, ys):
        """
        Ánh xạ hàng loạt (x, y) sang (lon, lat).
        - xs, ys: Mảng hoặc danh sách chỉ số cột và hàng.
        - Trả về: Danh sách (lon, lat).
        """
        xs = np.asarray(xs)
        ys = np.asarray(ys)
        
        # Kiểm tra giới hạn
        valid = (xs >= 0) & (xs < self.cols) & (ys >= 0) & (ys < self.rows)
        if not valid.all():
            raise ValueError("Một số chỉ số ngoài phạm vi lưới")
        
        lons = self.x_corner + xs * self.cellsize
        lats = abs(self.y_corner) - ys * self.cellsize
        return list(zip(lons, lats))


class SolidData():
    def __init__(self, M, rows, cols, x_corner, y_corner, cellsize, name, description="Unknown"):
        self.M, self.rows, self.cols, self.x_corner, self.y_corner, self.cellsize = M, rows, cols, x_corner, y_corner, cellsize
        self.name = name
        self.description = description
        self.mapper = LonLatMapper(self.x_corner, self.y_corner, self.cellsize, self.rows, self.cols)

    def __getitem__(self, key):
        """
        Truy cập ma trận thưa hoặc metadata qua toán tử [].
        - key là tuple (i,j): Trả về giá trị M[i,j] (hoặc 0 nếu không tồn tại). i, j là lon, lat
        """
        if isinstance(key, tuple):
            if self.M is None:
                raise ValueError("Ma trận chưa được tải. Gọi load_data() trước.")
            x, y = self.mapper.lonlat2xy(key[0], key[1])
            return self.M[y, x]  # Trả về giá trị tại (i,j), 0 nếu không có
        else:
            raise TypeError("Khóa phải là tuple (lon, lat)")
    
    @staticmethod
    def read_asc(file_path, name, dtype='int', description="Unknown"):
        # Đọc metadata từ header
        with open(file_path, "r") as file:
            cols = int(file.readline().split()[1])
            rows = int(file.readline().split()[1])
            x_corner = float(file.readline().split()[1])
            y_corner = float(file.readline().split()[1])
            cellsize = float(file.readline().split()[1])
            nodata_val = float(file.readline().split()[1])  # Giả sử nodata là số

        # Đọc dữ liệu dưới dạng mảng NumPy (bỏ qua 6 dòng header)
        data = np.loadtxt(file_path, skiprows=6, dtype=np.float64)

        # Xử lý giá trị nodata và chuyển đổi sang ma trận thưa
        mask = (data != nodata_val)
        if dtype == 'int':
            data = data.astype(np.int64)
        elif dtype == 'float':
            data = data.astype(np.float64)

        # Tạo ma trận thưa (dok_matrix hoặc lil_matrix)
        M = dok_matrix((rows, cols), dtype=data.dtype)
        rows_idx, cols_idx = np.where(mask)
        M[rows_idx, cols_idx] = data[rows_idx, cols_idx]

        return SolidData(M, rows, cols, x_corner, y_corner, cellsize, name, description)
            
    def save_dok_matrix(self, output_dir):
        """
        Lưu ma trận dok_matrix và metadata vào thư mục output_dir.
        - output_dir: Thư mục lưu tệp.
        - Tệp ma trận: <tên thư mục>.npz.
        - Tệp metadata: metadata.json.
        """
        print("Bắt đầu lưu dữ liệu: ")
        # Lấy tên thư mục từ output_dir
        folder_name = os.path.basename(os.path.normpath(output_dir))
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(output_dir, exist_ok=True)
        
        # Đường dẫn tệp
        matrix_path = os.path.join(output_dir, f"{folder_name}.npz")
        metadata_path = os.path.join(output_dir, "metadata.json")
        
        # Chuyển dok_matrix sang csr_matrix để lưu
        M_csr = self.M.tocsr()
        save_npz(matrix_path, M_csr)
        
        # Lưu metadata
        metadata = {
            'name'   : self.name,
            'rows'   : self.rows,
            'cols'   : self.cols,
            'x_corner': self.x_corner,
            'y_corner': self.y_corner,
            'cellsize': self.cellsize,
            'description' : self.description
        }
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
    
    @staticmethod
    def load_dok_matrix(input_dir):
        """
        Đọc ma trận dok_matrix và metadata từ thư mục input_dir.
        - input_dir: Thư mục chứa tệp <tên thư mục>.npz và metadata.json.
        - Trả về: (M, x_corner, y_corner, cellsize)
        """
        # Lấy tên thư mục từ input_dir
        folder_name = os.path.basename(os.path.normpath(input_dir))
        
        # Đường dẫn tệp
        matrix_path = os.path.join(input_dir, f"{folder_name}.npz")
        metadata_path = os.path.join(input_dir, "metadata.json")
        
        # Đọc ma trận
        M_csr = load_npz(matrix_path)
        M = M_csr.todok()  # Chuyển lại dok_matrix
        
        # Đọc metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        rows = metadata['rows']
        cols = metadata['cols']
        x_corner = metadata['x_corner']
        y_corner = metadata['y_corner']
        cellsize = metadata['cellsize']
        description = metadata['description']
        name = metadata['name']
        data = SolidData(M, rows, cols, x_corner, y_corner, cellsize, name, description)
        return data

    def sparse2dict(self):
        sparse_dict = {
            'lon': [],
            'lat': [],
            self.name: [],
        }

        llmapper = LonLatMapper(self.x_corner, self.y_corner, self.cellsize, self.rows, self.cols)
        for i in tqdm(self.M.items()):
            y, x  = i[0]
            lon, lat = llmapper.xy2lonlat(x, y)
            sparse_dict['lon'].append(lon)
            sparse_dict['lat'].append(lat)
            sparse_dict[self.name].append(i[1])
        return sparse_dict
    
    def plot(self, output_file=None):
        import matplotlib.pyplot as plt
        import vaex
        
        data_dict = self.sparse2dict()
        df = vaex.from_dict(data_dict)
        df.viz.heatmap(df.lon, df.lat, what=vaex.stat.mean(getattr(df, self.name)))
        if output_file:
            print("Bắt đầu lưu biểu đồ")
            folder_name = os.path.dirname(output_file)
            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(folder_name, exist_ok=True)
            plt.savefig(output_file)  # Lưu hình thành tệp
        else:
            print("Bắt đầu plot biểu đồ:")
            plt.show()
        plt.close()


