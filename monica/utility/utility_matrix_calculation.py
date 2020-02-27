from utility.utility_geographic_conversion import SurfaceVector, GeographicRectangleArea


class DensityMatrixQueueShapeSubArea:
    def __init__(self, start_index_x: float, start_index_y: float, delta_x: float, delta_y: float):
        self.start_index_x = int(start_index_x)
        self.start_index_y = int(start_index_y)
        self.end_index_x = int(start_index_x+delta_x)
        self.end_index_y = int(start_index_y+delta_y)

    def set_properties(self, start_index_x: float, start_index_y: float, end_index_x: float, end_index_y: float):
        self.start_index_x = start_index_x
        self.start_index_y = start_index_y
        self.end_index_x = end_index_x
        self.end_index_y = end_index_y


class UtilityMatrixCalculation:
    @staticmethod
    def chipping_value(ref_value: int, value_max: int):
        if ref_value<=value_max:
            return ref_value

        return value_max

    @staticmethod
    def calculate_numberpeople_queueshapearea(density_matrix,density_matrix_queue_shape_subarea):
        try:
            matrix_size = density_matrix.shape
            max_num_row = min(matrix_size[0], density_matrix_queue_shape_subarea.end_index_x)
            max_num_col = min(matrix_size[1], density_matrix_queue_shape_subarea.end_index_y)

            counter_people_subarea = 0

            for index_row in range(density_matrix_queue_shape_subarea.start_index_x,max_num_row):
                for index_col in range(density_matrix_queue_shape_subarea.start_index_y,max_num_col):
                    if density_matrix[index_row, index_col] != -1:
                        counter_people_subarea = counter_people_subarea+density_matrix[index_row,index_col]

            return counter_people_subarea

        except Exception as ex:
            return 0


class DensityMatrixStatistics:
    def __init__(self):
        self.counter_total_cells=0
        self.counter_not_monitored_area = 0
        self.counter_zero_cells=0
        self.counter_verylow_cells=0
        self.counter_low_cells=0
        self.counter_significant_cells=0
        self.percentage_not_covered=0
        self.percentage_cells_zero=0
        self.percentage_verylow_cells=0
        self.percentage_low_cells=0
        self.percentage_significant_cells=0
        self.size_matrix_x=0
        self.size_matrix_y=0
        self.numpy_densitymap=None

    def calculate_statistics(self,density_matrix_origin,very_low_threshold,low_threshold,significant_threshold):
        try:
            self.counter_not_monitored_area = 0
            self.counter_zero_cells = 0
            self.counter_verylow_cells = 0
            self.counter_low_cells=0
            self.counter_significant_cells=0
            self.numpy_densitymap=density_matrix_origin
            matrix_origin_size=density_matrix_origin.shape
            num_row_big=matrix_origin_size[0]
            num_col_big=matrix_origin_size[1]
            for index_row in range(0,num_row_big):
                for index_col in range(0,num_col_big):
                    if density_matrix_origin[index_row,index_col]==-1:
                        self.counter_not_monitored_area = self.counter_not_monitored_area+1
                    elif density_matrix_origin[index_row,index_col]==0:
                        self.counter_zero_cells = self.counter_zero_cells+1
                    elif density_matrix_origin[index_row,index_col]>0 and density_matrix_origin[index_row,index_col]<very_low_threshold:
                        self.counter_verylow_cells = self.counter_verylow_cells+1
                    elif density_matrix_origin[index_row,index_col]>very_low_threshold and density_matrix_origin[index_row,index_col]<low_threshold:
                        self.counter_low_cells = self.counter_low_cells+1
                    elif density_matrix_origin[index_row,index_col]>significant_threshold:
                        self.counter_significant_cells = self.counter_significant_cells+1

            self.size_matrix_x=num_col_big
            self.size_matrix_y=num_row_big
            self.counter_total_cells = num_row_big*num_col_big
            self.percentage_not_covered = self.counter_not_monitored_area/self.counter_total_cells
            self.percentage_cells_zero=self.counter_zero_cells/self.counter_total_cells
            self.percentage_verylow_cells=self.counter_verylow_cells/self.counter_total_cells
            self.percentage_significant_cells=self.counter_significant_cells/self.counter_total_cells
        except Exception as ex:
            return