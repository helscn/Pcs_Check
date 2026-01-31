import math

class GridData:
    def __init__(self, cell_size, points=None):
        """将空间划分为网格"""
        self.cell_size = cell_size
        self.grid = {}
        if points:
            for point in points:
                self.add(point)
    
    def _get_xy(self, point):
        """获取点的坐标"""
        if hasattr(point, 'x') and hasattr(point, 'y'):
            x, y = point.x, point.y
        else:
            x = point[0]
            y = point[1]
        return x, y

    def __iter__(self):
        """使GridData可迭代：遍历所有点"""
        for cell_coord, points_in_cell in self.grid.items():
            for point in points_in_cell:
                yield point
    
    def __len__(self):
        """返回总点数"""
        return sum(len(points) for points in self.grid.values())

    def __contains__(self, point):
        """检查点是否在网格中"""
        x, y = self._get_xy(point)
        grid_x, grid_y = int(x // self.cell_size), int(y // self.cell_size)
        
        if (grid_x, grid_y) not in self.grid:
            return False
        
        # 注意：这里使用==比较，对于自定义对象需要确保实现了__eq__方法
        return point in self.grid[(grid_x, grid_y)]
    
    def add(self,point):
        """添加点"""
        x , y = self._get_xy(point)
        grid_x, grid_y = int(x // self.cell_size), int(y // self.cell_size)
        if (grid_x, grid_y) not in self.grid:
            self.grid[(grid_x, grid_y)] = []
        self.grid[(grid_x, grid_y)].append((point))

    def get_all_points(self):
        """获取所有点的列表"""
        return list(self)
    def query_radius(self, point, radius):
        """查询半径内的点"""
        result = []
        x, y = self._get_xy(point)
        
        # 计算需要检查的网格范围
        min_grid_x = int((x - radius) // self.cell_size)
        max_grid_x = int((x + radius) // self.cell_size)
        min_grid_y = int((y - radius) // self.cell_size)
        max_grid_y = int((y + radius) // self.cell_size)
        
        # 只检查相关网格
        for grid_x in range(min_grid_x, max_grid_x + 1):
            for grid_y in range(min_grid_y, max_grid_y + 1):
                if (grid_x, grid_y) in self.grid:
                    for p in self.grid[(grid_x, grid_y)]:
                        px, py = self._get_xy(p)
                        dist = math.sqrt((px-x)**2 + (py-y)**2)
                        if dist <= radius:
                            result.append((px, py))
        return result
    
