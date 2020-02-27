from typing import List, Tuple
from enum import Enum
from utility.geodesy import GeoPosition, ENUCoordinates, SurfaceVector, PolarCoordinates, GeoTranslations
import logging

logger = logging.getLogger('textlogger')


class VertexType(Enum):
    SHAPEPOINT = 1
    BORDERPOINT = 2


class VertexPositionHeading(Enum):
    HEADING_LEFT = 1,
    HEADING_RIGHT = 2


class VertexPositionHeigth(Enum):
    HEIGHT_TOP = 1,
    HEIGT_MIDDLE = 0,
    HEIGHT_BOTTOM = 2


class DensityMapConfiguration(object):
    def __init__(self,
                 ground_plane_position: GeoPosition,
                 bearing_map: float = 0,
                 number_rows: int = 0,
                 number_cols: int = 0,
                 cell_size_row: int = 1,
                 cell_size_col: int = 1):
        self.ground_plane_position = ground_plane_position
        self.bearing_map = bearing_map
        self.number_rows = number_rows
        self.number_cols = number_cols
        self.cell_size_row = cell_size_row
        self.cell_size_col = cell_size_col


class MatrixCoords(object):
    def __init__(self, brow_idx: int, index_col: int):
        self.brow_idx = brow_idx
        self.index_col = index_col

    def to_tuple(self) -> Tuple[int, int]:
        return self.index_col, self.brow_idx

    def to_enu_coordinates(self,
                           density_map_conf: DensityMapConfiguration) \
            -> ENUCoordinates:
        if not density_map_conf:
            return None
        try:
            distance_east_m_0 = self.brow_idx * density_map_conf.cell_size_col
            distance_north_m_0 = self.index_col * density_map_conf.cell_size_row
            up_m = 0

            polar_coordinates = PolarCoordinates()
            polar_coordinates.set_surface_coordinates(surface_vector=SurfaceVector(x=distance_east_m_0,
                                                                                   y=distance_north_m_0))

            rotation_enu = -1*density_map_conf.bearing_map

            polar_coordinates.add_rotation_angle(rotation=rotation_enu)
            surface_vector = polar_coordinates.convert_surface_coordinate()

            return ENUCoordinates(east=surface_vector.x,
                                  north=surface_vector.y,
                                  up=up_m)
        except Exception as ex:
            return None

    def to_geoposition_coordinates(self,
                                   density_map_conf: DensityMapConfiguration
                                   ) \
            -> GeoPosition:
        if not density_map_conf:
            return None
        try:
            enu_pos = self.to_enu_coordinates(density_map_conf=density_map_conf)

            (latitude, longitude, altitude) = GeoTranslations.enu2llh(east=enu_pos.east,
                                                                      north=enu_pos.north,
                                                                      up=enu_pos.up,
                                                                      org_lat=density_map_conf.ground_plane_position.latitude,
                                                                      org_long=density_map_conf.ground_plane_position.longitude)

            return GeoPosition(latitude=latitude,
                               longitude=longitude,
                               altitude=altitude)

        except Exception as ex:
            print(ex)
            return None

    def __eq__(self, other: "MatrixCoords") -> bool:
        if not other:
            return False

        if other.brow_idx != self.brow_idx:
            return False

        if other.index_col != self.index_col:
            return False

        return True

    def __ne__(self, other: "MatrixCoords"):
        return not self.__eq__(other=other)


class GroupMatrixCoords(object):
    def __init__(self,
                 list_vertex: List[MatrixCoords] = None):
        self.idx = 0
        self.list_vertex = list()

        if list_vertex:
            self.extend(list_vertex=list_vertex)

    def append(self, vertex: MatrixCoords) -> bool:
        try:
            if not vertex:
                return False

            self.list_vertex.append(vertex)
            return True
        except Exception as ex:
            logger.error('GroupMatrixCoords append Exception: {}'.format(ex))
            return False

    def extend(self, list_vertex: List[MatrixCoords]) -> bool:
        try:
            if not list_vertex:
                return False

            self.list_vertex.extend(list_vertex)
            return True
        except Exception as ex:
            logger.error('GroupMatrixCoords append Exception: {}'.format(ex))
            return False

    def empty(self) -> bool:
        if self.list_vertex:
            return False

        return True

    def get_listvertex(self) -> List[MatrixCoords]:
        return self.list_vertex

    def __iter__(self):
        return self

    def __next__(self):
        self.idx += 1
        try:
            return self.list_vertex[self.idx - 1]
        except IndexError:
            self.idx = 0
            raise StopIteration  # Done iterating.

    def __len__(self):
        return len(self.list_vertex)

    def consolidate_polygon(self) -> bool:
        try:
            if not self.list_vertex or len(self.list_vertex) == 1:
                return False

            first_vertex = self.list_vertex[0]
            last_vertex = self.list_vertex[-1]

            if (first_vertex is None) or (last_vertex is None):
                return False

            if first_vertex != last_vertex:
                self.list_vertex.append(first_vertex)

            return True
        except Exception as ex:
            logger.error('GroupMatrixCoords consolidate_polygon Exception: {}'.format(ex))
            return False

    def get_listpoints(self,
                       density_map_conf: DensityMapConfiguration,
                       vertex_position_heigth: VertexPositionHeigth = VertexPositionHeigth.HEIGHT_TOP) \
            -> List[GeoPosition]:
        try:
            if not density_map_conf or self.empty():
                return None

            list_geo_points = list()

            for vertex in self.get_listvertex():
                if len(self.list_vertex) > 1 and (len(self.list_vertex) == (len(list_geo_points)+1)):
                    geo_position = vertex.to_geoposition_coordinates(density_map_conf=density_map_conf,
                                                                     vertex_position_heigth=vertex_position_heigth,
                                                                     vertex_position_line=VertexPositionHeading.HEADING_RIGHT)
                else:
                    geo_position = vertex.to_geoposition_coordinates(density_map_conf=density_map_conf,
                                                                     vertex_position_heigth=vertex_position_heigth)
                list_geo_points.append(geo_position)

                if len(self.get_listvertex()) == 1:
                    geo_position = vertex.to_geoposition_coordinates(density_map_conf=density_map_conf,
                                                                     vertex_position_heigth=vertex_position_heigth,
                                                                     vertex_position_line=VertexPositionHeading.HEADING_RIGHT)
                    list_geo_points.append(geo_position)

            return list_geo_points
        except Exception as ex:
            logger.error('GroupMatrixCoords get_listpoints Exception: {}'.format(ex))
            return None


class ListGroupMatrixCoords(object):
    def __init__(self,
                 list_groupvertexes: List[GroupMatrixCoords] = None):
        self.idx = 0
        self.list_groupvertexes = list()
        self.extend(list_groupvertexes=list_groupvertexes)

    def extend(self, list_groupvertexes: List[GroupMatrixCoords]) -> bool:
        if not list_groupvertexes:
            return False

        self.list_groupvertexes.extend(list_groupvertexes)
        return True

    def append(self,
               group_vertexes: GroupMatrixCoords) \
            -> bool:
        if not group_vertexes:
            return False

        self.list_groupvertexes.append(group_vertexes)
        return True

    def get_listgroupvertex(self) -> List[GroupMatrixCoords]:
        return self.list_groupvertexes

    def __iter__(self):
        return self

    def __next__(self):
        self.idx += 1
        try:
            return self.list_groupvertexes[self.idx - 1]
        except IndexError:
            self.idx = 0
            raise StopIteration  # Done iterating.

    def __len__(self):
        return len(self.list_groupvertexes)


class MatrixCell(MatrixCoords):
    def __init__(self, brow_idx: int, index_col: int, count: int):
        self.brow_idx = brow_idx
        self.index_col = index_col
        self.count = count

    def to_matrixcoords(self) -> MatrixCoords:
        return MatrixCoords(brow_idx=self.brow_idx,
                           index_col=self.index_col)

    def __eq__(self, other: "MatrixCell") -> bool:
        if not other:
            return False

        if other.index_col == self.index_col and other.brow_idx == self.brow_idx and other.count==self.count:
            return True

        return False

    def get_count(self) -> int:
        return int(self.count)

    def check_is_adiacent(self, matrix_cell: "MatrixCell") -> bool:
        if not matrix_cell:
            return False

        if self.brow_idx != matrix_cell.brow_idx and self.index_col != matrix_cell.index_col:
            return False

        if self.brow_idx == matrix_cell.brow_idx and abs(self.index_col-matrix_cell.index_col) == 1:
            return True

        if self.index_col == matrix_cell.index_col and abs(self.brow_idx-matrix_cell.brow_idx) == 1:
            return True
        return False


class SingleRowAdiacentCells(object):
    def __init__(self):
        self.brow_idx = 0
        self.colstart = 0
        self.colstop = 0
        self.totalnumberelements = 0
        self.list_adiacent_cells = list()

    def consolidate_number_elements(self) -> bool:
        self.totalnumberelements = 0

        if self.empty():
            return False

        for cell in self.get_list_adiacent_cells():
            if not cell:
                continue

            self.totalnumberelements += cell.get_count()

        return True

    def get_all_shape_vertex(self) -> GroupMatrixCoords:
        shape_vertex_bottom_left = MatrixCoords(brow_idx=self.brow_idx + 1,
                                                index_col=self.colstart)
        shape_vertex_top_left = MatrixCoords(brow_idx=self.brow_idx,
                                             index_col=self.colstart)

        shape_vertex_top_right = MatrixCoords(brow_idx=self.brow_idx,
                                              index_col=self.colstop + 1)

        shape_vertex_bottom_right = MatrixCoords(brow_idx=self.brow_idx + 1,
                                                 index_col=self.colstop + 1)

        return GroupMatrixCoords(list_vertex=
        [
            shape_vertex_bottom_left,
            shape_vertex_top_left,
            shape_vertex_top_right,
            shape_vertex_bottom_right,
            shape_vertex_bottom_left
        ])

    def get_rowvertexes(self) -> GroupMatrixCoords:
        return GroupMatrixCoords(list_vertex=[MatrixCoords(brow_idx=self.brow_idx,
                                                    index_col=self.colstart),
                                        MatrixCoords(brow_idx=self.brow_idx,
                                                    index_col=self.colstop)])

    def get_list_adiacent_cells(self) -> List[MatrixCell]:
        return self.list_adiacent_cells

    def remove_cell(self, cell: MatrixCell) -> bool:
        if not cell:
            return False

        if cell not in self.list_adiacent_cells:
            return False

        self.list_adiacent_cells.remove(cell)
        self.totalnumberelements -= cell.count
        return False

    def check_cell_inside(self, cell: MatrixCell) -> bool:
        if not cell:
            return False

        if self.empty():
            return False

        for single_cell in self.get_list_adiacent_cells():
            if single_cell == cell:
                return True

        return False

    def check_cell_adiacent(self, cell: MatrixCell) -> bool:
        if not cell:
            return False

        if self.empty():
            return True

        for internal_cell in self.get_list_adiacent_cells():
            if not internal_cell:
                continue
            if cell.check_is_adiacent(matrix_cell=internal_cell):
                return True

        return False

    def empty(self) -> bool:
        if not self.list_adiacent_cells:
            return True

        return False

    def get_totalelements(self) -> int:
        return self.totalnumberelements

    def get_totalnumbercells(self) -> int:
        if not self.list_adiacent_cells:
            return 0

        return len(self.list_adiacent_cells)

    def check_indexcol_insideinterval(self, index_to_check: int) -> bool:
        if index_to_check < self.colstart:
            return False

        if index_to_check > self.colstop:
            return False

        return True

    def set_rowindex(self, brow_idx):
        self.brow_idx = brow_idx

    def check_row_issubrow(self, subrow_to_check: "SingleRowAdiacentCells") -> bool:
        if not subrow_to_check or subrow_to_check.empty():
            return False

        if subrow_to_check.get_totalnumbercells() > self.get_totalnumbercells():
            return False

        if subrow_to_check.get_totalelements() > self.get_totalelements():
            return False

        if self.brow_idx != subrow_to_check.brow_idx:
            return False

        if subrow_to_check.colstop < self.colstart:
            return False

        if subrow_to_check.colstart > self.colstop:
            return False

        if self.colstop < subrow_to_check.colstart:
            return False

        if self.colstart > subrow_to_check.colstop:
            return False

        return True

    @staticmethod
    def create_listrow_fromlistcells(list_cells: List[MatrixCell]) -> List["SingleRowAdiacentCells"]:
        if not list_cells:
            return None

        list_return_rows = list()
        single_row = SingleRowAdiacentCells()

        for cell in list_cells:
            if not cell:
                continue

            if not single_row.empty() and (not single_row.check_cell_adiacent(cell=cell)):
                list_return_rows.append(single_row)
                single_row = SingleRowAdiacentCells()

            single_row.add_cell(cell=cell)

        if single_row not in list_return_rows:
            list_return_rows.append(single_row)

        return list_return_rows

    def subtract_row(self, rowtosubtrackt: "SingleRowAdiacentCells") -> List["SingleRowAdiacentCells"]:
        try:
            if not rowtosubtrackt or rowtosubtrackt.empty():
                return [self]

            counter_removed = 0
            for cell in rowtosubtrackt.get_list_adiacent_cells():
                if not cell:
                    continue

                if not self.remove_cell(cell=cell):
                    continue

                counter_removed += 1

            if counter_removed == 0:
                return [self]

            return SingleRowAdiacentCells.create_listrow_fromlistcells(list_cells=self.list_adiacent_cells)
        except Exception as ex:
            print('subtract_row Exception: {}'.format(ex))
            return None

    def check_is_row_adiacent(self, single_row: "SingleRowAdiacentCells") -> bool:
        if not single_row:
            return False

        if single_row.brow_idx < self.brow_idx - 1 or \
            single_row.brow_idx > self.brow_idx + 1:
            return False

        if single_row.brow_idx == self.brow_idx:
            if single_row.colstart == self.colstop + 1:
                return True

            if single_row.colstop == self.colstart - 1:
                return True

            return False

        if single_row.check_indexcol_insideinterval(index_to_check=self.colstart):
            return True

        if single_row.check_indexcol_insideinterval(index_to_check=self.colstop):
            return True

        if self.check_indexcol_insideinterval(index_to_check=single_row.colstart):
            return True

        if self.check_indexcol_insideinterval(index_to_check=single_row.colstop):
            return True

        return False

    def add_cell(self, cell: MatrixCell) -> bool:
        try:
            if not cell:
                return False

            if not self.list_adiacent_cells:
                self.brow_idx = cell.brow_idx
                self.colstart = cell.index_col

            if cell.index_col > self.colstop:
                self.colstop = cell.index_col

            self.list_adiacent_cells.append(cell)

            return True
        except Exception as ex:
            return False

    def get_specific_matrixcell(self, index_cell: int = 0) -> MatrixCell:
        if not self.list_adiacent_cells:
            return None

        if index_cell >= self.get_matrixcell_count():
            return None

        return self.list_adiacent_cells[index_cell]

    def remove_duplicates(self) -> bool:
        try:
            if self.empty():
                return False

            for index_cell_start in range(0, len(self.list_adiacent_cells)-1):
                cell_start = self.list_adiacent_cells[index_cell_start]

                if not cell_start:
                    continue

                for index_cell_end in range(index_cell_start+1, len(self.list_adiacent_cells)):
                    cell_end = self.list_adiacent_cells[index_cell_end]

                    if not cell_end:
                        continue

                    if cell_start != cell_end:
                        continue

                    self.list_adiacent_cells.remove(cell_end)

                return True
        except Exception as ex:
            logger.error('SingleRowAdiacentCells remove_duplicate Exception: {}'.format(ex))
            return False


class RegionAdiacentCells(object):
    def __init__(self):
        self.list_rowadiacentcells = list()
        self.start_row_index = 0
        self.end_row_index = 0
        self.totalnumber_elements = 0
        self.totalnumber_cells = 0
        self.mean_element = 0

    def consolidate_totalnumber_elements(self) -> bool:
        try:
            if self.empty():
                return False

            self.totalnumber_elements = 0
            self.totalnumber_cells = 0

            for row in self.get_list_rows():
                if not row:
                    continue

                row.remove_duplicates()
                row.consolidate_number_elements()
                self.totalnumber_elements += row.get_totalelements()
                self.totalnumber_cells += row.get_totalnumbercells()

            self.mean_element = int(self.totalnumber_elements/self.totalnumber_cells)

            return True
        except Exception as ex:
            return False

    def get_vertexes(self, vertex_type: VertexType):
        if vertex_type == vertex_type.SHAPEPOINT:
            return self.get_shapevertexes()

        return self.get_bordervertexes()

    def get_shapevertexes(self) -> GroupMatrixCoords:
        try:
            if self.empty():
                return None

            list_shapevertexes = list()

            for row in self.get_list_rows():
                if not row or row.empty():
                    continue

                list_cells = row.get_list_adiacent_cells()

                if not list_cells:
                    continue

                list_rowvertex = list()

                for cell in list_cells:
                    if not cell:
                        continue

                    list_rowvertex.append(cell.to_matrixcoords())

                list_shapevertexes.extend(list_rowvertex)

            return GroupMatrixCoords(list_vertex=list_shapevertexes)
        except Exception as ex:
            print('get_shapevertexes Exception: {}'.format(ex))
            return None

    def get_bordervertexes(self) -> GroupMatrixCoords:
        try:
            if self.empty():
                return None

            list_shapevertexes = list()

            for row in self.get_list_rows():
                if not row or row.empty():
                    continue

                list_vertexes = row.get_rowvertexes()

                if not list_vertexes:
                    continue

                list_shapevertexes.extend(list_vertexes)

            return GroupMatrixCoords(list_vertex=list_shapevertexes)
        except Exception as ex:
            print('get_shapevertexes Exception: {}'.format(ex))
            return None

    @staticmethod
    def check_cell_inside_list_region(list_regions: List["RegionAdiacentCells"], cell: MatrixCell) -> bool:
        if not cell or not list_regions:
            return False

        for region in list_regions:
            if not region:
                continue

            if region.check_cell_inside(cell=cell):
                return True

        return False

    def check_cell_inside(self, cell: MatrixCell) -> bool:
        if not cell:
            return False
        try:
            if self.empty():
                return False

            for single_row in self.get_list_rows():
                if not single_row:
                    continue

                if single_row.check_cell_inside(cell=cell):
                    return True

            return False
        except Exception:
            return False

    def get_count_element(self) -> int:
        return self.totalnumber_elements

    def get_count_cells(self) -> int:
        return self.totalnumber_cells

    def get_list_rows(self) -> List[SingleRowAdiacentCells]:
        return self.list_rowadiacentcells

    def get_list_adiacent_cells(self) -> List[MatrixCell]:
        if not self.list_rowadiacentcells:
            return None

        list_adiacent_cells = list()

        for row in self.get_list_rows():
            if not row or not row.list_adiacent_cells:
                continue

            list_adiacent_cells.extend(row.list_adiacent_cells)

        return list_adiacent_cells

    def get_future_mean(self, matrix_cell: MatrixCell) -> float:
        if not matrix_cell:
            return 0.0

        if self.empty():
            return float(matrix_cell.count)

        return float(self.totalnumber_elements + matrix_cell.count)/float(len(self.list_adiacent_cells)+1)

    def get_mean(self) -> int:
        return self.mean_element

    def get_matrixcell_count(self) -> int:
        if self.empty():
            return 0

        return len(self.get_list_adiacent_cells())

    def remove_matrixcell(self, matrix_cell: MatrixCell) -> bool:
        if not matrix_cell:
            return False

        if self.empty():
            return False

        if matrix_cell not in self.list_adiacent_cells:
            return False

        self.list_adiacent_cells.remove(matrix_cell)
        return True

    def get_max_rowsize(self):
        return self.end_row_index - self.start_row_index + 1

    def get_max_columnsize(self):
        return  self.indexcol_end-self.indexcol_start+1

    def get_expectedcells_completerectangle(self):
        return self.get_max_rowsize() * self.get_max_columnsize()

    def empty(self) -> bool:
        if not self.list_rowadiacentcells:
            return True

        if len(self.list_rowadiacentcells) == 0:
            return True

        return False

    def add_singlerow_adiacent(self, single_row: SingleRowAdiacentCells) -> bool:
        if not single_row:
            return False

        if not self.list_rowadiacentcells:
            self.start_row_index = single_row.brow_idx

        self.list_rowadiacentcells.append(single_row)
        self.totalnumber_elements += single_row.get_totalelements()
        self.totalnumber_cells += single_row.get_totalnumbercells()

        if single_row.brow_idx > self.end_row_index:
            self.end_row_index = single_row.brow_idx

    def check_is_rowadiacent(self, row_to_check: SingleRowAdiacentCells) -> bool:
        if not row_to_check:
            return False

        if self.empty():
            return True

        if row_to_check.brow_idx > self.end_row_index+1 or \
                row_to_check.brow_idx < self.start_row_index-1:
            return False

        for row in self.get_list_rows():
            if row.check_is_row_adiacent(single_row=row_to_check):
                return True

        return False  # FIXME: Check Again

    def get_rowshapesvertex(self) -> ListGroupMatrixCoords:
        try:
            shape_global_vertex = ListGroupMatrixCoords()

            for row in self.get_list_rows():
                if not row:
                    continue

                shape_vertex_row = row.get_all_shape_vertex()

                if not shape_vertex_row:
                    continue

                shape_global_vertex.append(shape_vertex_row)

            return shape_global_vertex
        except Exception as ex:
            print(ex)
            return None


class GroupRegionsAdiacentCells(object):
    def __init__(self,
                 list_regions: List[RegionAdiacentCells] = None):
        self.idx = 0
        self.list_regions = list()
        self.extend(list_regions=list_regions)

    def empty(self) -> bool:
        if not self.list_regions:
            return True

        return False

    def extend(self, list_regions: List[RegionAdiacentCells]) -> bool:
        if not list_regions:
            return False

        self.list_regions.extend(list_regions)
        return True

    def append(self, region: RegionAdiacentCells) -> bool:
        if not region:
            return False

        self.list_regions.append(region)
        return True

    def get_listregions(self) -> List[RegionAdiacentCells]:
        return self.list_regions

    def get_globallistgroupvertexes(self, vertex_type: VertexType) -> ListGroupMatrixCoords:
        try:
            if self.empty():
                return None

            list_groupvertex = ListGroupMatrixCoords()

            for region in self.get_listregions():
                if not region:
                    continue

                group_shapevertexes = region.get_vertexes(vertex_type=vertex_type)

                if not group_shapevertexes:
                    continue

                list_groupvertex.append(group_shapevertexes)

            return list_groupvertex
        except Exception as ex:
            print('get_globallistgroupvertexes Exception: {}'.format(ex))
            return None

    def check_cell_inside_list_region(self, cell: MatrixCell) -> bool:
        if not cell or self.empty():
            return False

        for region in self.get_listregions():
            if not region:
                continue

            if region.check_cell_inside(cell=cell):
                return True

        return False

    def __iter__(self):
        return self

    def __next__(self):
        self.idx += 1
        try:
            return self.list_regions[self.idx - 1]
        except IndexError:
            self.idx = 0
            raise StopIteration  # Done iterating.

    def __len__(self):
        return len(self.list_regions)

    def consolidate_regions(self) -> bool:
        if self.empty():
            return False

        for region in self.get_listregions():
            if not region:
                continue

            region.consolidate_totalnumber_elements()
        return True

    def convert_to_list_shapes(self) -> ListGroupMatrixCoords:
        try:
            if self.empty():
                return None

            list_shapes = ListGroupMatrixCoords()

            for region in self.get_listregions():
                if not region:
                    continue

                shape = region.convert_region_to_shapevertex()

                if not shape:
                    continue

                list_shapes.append(group_vertexes=shape)
            return list_shapes
        except:
            return None
