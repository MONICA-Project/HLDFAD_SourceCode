from rest_framework import serializers  # , relations
from jobs.models import CrowdHeatmapOutput


class CrowdHeatmapOutputSerializer(serializers.ModelSerializer):  # GeoFeatureModelSerializer
    def create(self, validated_data):
        crowd_heatmap_serialized = CrowdHeatmapOutput.objects.create(**validated_data)

        return crowd_heatmap_serialized

    def update(self, instance, validated_data):
        try:
            instance.density_map                = validated_data.get('density_map',
                                                                     instance.density_map)
            instance.timestamp                  = validated_data.get('timestamp',
                                                                     instance.timestamp.isoformat())
            instance.ground_plane_position      = validated_data.get('ground_plane_position',
                                                                     instance.ground_plane_position)
            instance.ground_plane_orientation   = validated_data.get('ground_plane_orientation',
                                                                     instance.ground_plane_orientation)
            instance.cell_size_m                = validated_data.get('cell_size_m',
                                                                     instance.cell_size_m)
            instance.num_cols                   = validated_data.get('num_cols',
                                                                     instance.num_cols)
            instance.num_rows                   = validated_data.get('num_rows',
                                                                     instance.num_rows)
            instance.global_people_counting     = validated_data.get('global_people_counting',
                                                                     instance.global_people_counting)
            instance.confidence_level           = validated_data.get('confidence_level',
                                                                     instance.confidence_level)
            instance.localization_counter_registered = validated_data.get('localization_counter_registered',
                                                                          instance.localization_counter_registered)
            instance.localization_counter_active = validated_data.get('localization_counter_active',
                                                                       instance.localization_counter_active)
            instance.save()

            return instance
        except Exception as ex:
            return None

    @classmethod
    def from_json(cls, json_data):
        deserializer = CrowdHeatmapOutputSerializer(data=json_data)

        if not deserializer.is_valid():
            return False

        return cls(CrowdHeatmapOutput(**deserializer.validated_data))

        # return cls(json_data)
        # or something like:
        # instance = cls()
        # instance.attr1 = json_data['attr1']
        # ...

    # def to_json(self):
    #     return UtilitySerializer.convert_serializer_to_json(self.serializer)

    class Meta:
        model = CrowdHeatmapOutput
        #geo_field = 'ground_plane_position'

        fields = ('density_map',
                  'timestamp',
                  'ground_plane_position',
                  'ground_plane_orientation',
                  'cell_size_m',
                  'num_cols',
                  'num_rows',
                  'global_people_counting',
                  'confidence_level',
                  'localization_counter_registered',
                  'localization_counter_active'
                  )


# class CrowdHeatmapOutputSerializer(serializers.ModelSerializer):
#     def create(self, validated_data):
#         crowd_heatmap_serialized = CrowdHeatmapOutput.objects.create(**validated_data)
#
#         return crowd_heatmap_serialized
#
#     class Meta:
#         model = CrowdHeatmapOutput
#         #geo_field = 'ground_plane_position'
#         fields = ('density_map','timestamp','ground_plane_orientation','cell_size_m','num_cols','num_rows','global_people_counting','confidence_level')

# class GateCountingObservationSerializer(serializers.ModelSerializer):
#
#     def create(self, validated_data):
#         obs_data = GateCountingObservation.objects.create(**validated_data)
#         return obs_data
#
#     class Meta:
#         model = GateCountingObservation