<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Symbology|Labeling" version="3.40.5-Bratislava" labelsEnabled="1">
  <renderer-v2 forceraster="0" referencescale="-1" type="RuleRenderer" symbollevels="0" enableorderby="0">
    <rules key="{1c3604c6-4654-4249-ba2b-2873159958c2}">
      <rule label="Vértices" key="{324bda6b-3296-4d35-ab39-0ba34b525dd1}" symbol="0"/>
      <rule label="Distâncias" key="{9c60d1d1-614c-47df-8acb-3444f2137717}" symbol="1"/>
      <rule label="Azimutes" key="{626271a3-13c1-48dc-b69a-db246e1b6fa9}" symbol="2"/>
      <rule label="Área" key="{3cabcc2c-03c1-4bc2-8f3e-291d0a7ad946}" symbol="3"/>
    </rules>
    <symbols>
      <symbol type="fill" name="0" force_rhr="0" alpha="1" clip_to_extent="1" is_animated="0" frame_rate="10">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" class="GeometryGenerator" pass="2" id="{2db9fa64-f864-4d54-9d37-3d618846d768}">
          <Option type="Map">
            <Option type="QString" value="Marker" name="SymbolType"/>
            <Option type="QString" value="nodes_to_points( $geometry)" name="geometryModifier"/>
            <Option type="QString" value="MapUnit" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol type="marker" name="@0@0" force_rhr="0" alpha="1" clip_to_extent="1" is_animated="0" frame_rate="10">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" locked="0" class="FontMarker" pass="0" id="{1de64750-f530-4349-bcfa-1c62f3b89159}">
              <Option type="Map">
                <Option type="QString" value="0" name="angle"/>
                <Option type="QString" value="A" name="chr"/>
                <Option type="QString" value="31,31,31,255,rgb:0.12156862745098039,0.12156862745098039,0.12156862745098039,1" name="color"/>
                <Option type="QString" value="Arial Black" name="font"/>
                <Option type="QString" value="Normal" name="font_style"/>
                <Option type="QString" value="1" name="horizontal_anchor_point"/>
                <Option type="QString" value="bevel" name="joinstyle"/>
                <Option type="QString" value="0,-9" name="offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="Point" name="offset_unit"/>
                <Option type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" name="outline_color"/>
                <Option type="QString" value="0" name="outline_width"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale"/>
                <Option type="QString" value="MM" name="outline_width_unit"/>
                <Option type="QString" value="10" name="size"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="size_map_unit_scale"/>
                <Option type="QString" value="Point" name="size_unit"/>
                <Option type="QString" value="1" name="vertical_anchor_point"/>
              </Option>
              <effect enabled="1" type="effectStack">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option type="QString" value="13" name="blend_mode"/>
                    <Option type="QString" value="2.645" name="blur_level"/>
                    <Option type="QString" value="MM" name="blur_unit"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="blur_unit_scale"/>
                    <Option type="QString" value="0,0,0,255,rgb:0,0,0,1" name="color"/>
                    <Option type="QString" value="2" name="draw_mode"/>
                    <Option type="QString" value="0" name="enabled"/>
                    <Option type="QString" value="135" name="offset_angle"/>
                    <Option type="QString" value="2" name="offset_distance"/>
                    <Option type="QString" value="MM" name="offset_unit"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_unit_scale"/>
                    <Option type="QString" value="1" name="opacity"/>
                  </Option>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option type="QString" value="0" name="blend_mode"/>
                    <Option type="QString" value="1" name="blur_level"/>
                    <Option type="QString" value="MM" name="blur_unit"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="blur_unit_scale"/>
                    <Option type="QString" value="69,116,40,255,rgb:0.27058823529411763,0.45490196078431372,0.15686274509803921,1" name="color1"/>
                    <Option type="QString" value="188,220,60,255,rgb:0.73725490196078436,0.86274509803921573,0.23529411764705882,1" name="color2"/>
                    <Option type="QString" value="0" name="color_type"/>
                    <Option type="QString" value="ccw" name="direction"/>
                    <Option type="QString" value="0" name="discrete"/>
                    <Option type="QString" value="2" name="draw_mode"/>
                    <Option type="QString" value="1" name="enabled"/>
                    <Option type="QString" value="0.5" name="opacity"/>
                    <Option type="QString" value="gradient" name="rampType"/>
                    <Option type="QString" value="255,255,0,255,rgb:1,1,0,1" name="single_color"/>
                    <Option type="QString" value="rgb" name="spec"/>
                    <Option type="QString" value="2.5" name="spread"/>
                    <Option type="QString" value="MM" name="spread_unit"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="spread_unit_scale"/>
                  </Option>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option type="QString" value="0" name="blend_mode"/>
                    <Option type="QString" value="2" name="draw_mode"/>
                    <Option type="QString" value="1" name="enabled"/>
                    <Option type="QString" value="1" name="opacity"/>
                  </Option>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option type="QString" value="13" name="blend_mode"/>
                    <Option type="QString" value="2.645" name="blur_level"/>
                    <Option type="QString" value="MM" name="blur_unit"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="blur_unit_scale"/>
                    <Option type="QString" value="0,0,0,255,rgb:0,0,0,1" name="color"/>
                    <Option type="QString" value="2" name="draw_mode"/>
                    <Option type="QString" value="0" name="enabled"/>
                    <Option type="QString" value="135" name="offset_angle"/>
                    <Option type="QString" value="2" name="offset_distance"/>
                    <Option type="QString" value="MM" name="offset_unit"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_unit_scale"/>
                    <Option type="QString" value="1" name="opacity"/>
                  </Option>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option type="QString" value="0" name="blend_mode"/>
                    <Option type="QString" value="2.645" name="blur_level"/>
                    <Option type="QString" value="MM" name="blur_unit"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="blur_unit_scale"/>
                    <Option type="QString" value="69,116,40,255,rgb:0.27058823529411763,0.45490196078431372,0.15686274509803921,1" name="color1"/>
                    <Option type="QString" value="188,220,60,255,rgb:0.73725490196078436,0.86274509803921573,0.23529411764705882,1" name="color2"/>
                    <Option type="QString" value="0" name="color_type"/>
                    <Option type="QString" value="ccw" name="direction"/>
                    <Option type="QString" value="0" name="discrete"/>
                    <Option type="QString" value="2" name="draw_mode"/>
                    <Option type="QString" value="0" name="enabled"/>
                    <Option type="QString" value="0.5" name="opacity"/>
                    <Option type="QString" value="gradient" name="rampType"/>
                    <Option type="QString" value="255,255,255,255,rgb:1,1,1,1" name="single_color"/>
                    <Option type="QString" value="rgb" name="spec"/>
                    <Option type="QString" value="2" name="spread"/>
                    <Option type="QString" value="MM" name="spread_unit"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="spread_unit_scale"/>
                  </Option>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option type="Map" name="properties">
                    <Option type="Map" name="char">
                      <Option type="bool" value="true" name="active"/>
                      <Option type="QString" value="if (@geometry_part_num =  @geometry_part_count , '',&#xd;&#xa;'V-' ||  lpad( @geometry_part_num  ,2, '0')&#xd;&#xa;)" name="expression"/>
                      <Option type="int" value="3" name="type"/>
                    </Option>
                  </Option>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
            <layer enabled="1" locked="0" class="SimpleMarker" pass="0" id="{47dc65d1-9987-45fb-a73c-c71375cbf38b}">
              <Option type="Map">
                <Option type="QString" value="0" name="angle"/>
                <Option type="QString" value="square" name="cap_style"/>
                <Option type="QString" value="31,31,31,255,rgb:0.12156862745098039,0.12156862745098039,0.12156862745098039,1" name="color"/>
                <Option type="QString" value="1" name="horizontal_anchor_point"/>
                <Option type="QString" value="bevel" name="joinstyle"/>
                <Option type="QString" value="square" name="name"/>
                <Option type="QString" value="0,0" name="offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" name="outline_color"/>
                <Option type="QString" value="solid" name="outline_style"/>
                <Option type="QString" value="0" name="outline_width"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale"/>
                <Option type="QString" value="MM" name="outline_width_unit"/>
                <Option type="QString" value="diameter" name="scale_method"/>
                <Option type="QString" value="1" name="size"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="size_map_unit_scale"/>
                <Option type="QString" value="MM" name="size_unit"/>
                <Option type="QString" value="1" name="vertical_anchor_point"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol type="fill" name="1" force_rhr="0" alpha="1" clip_to_extent="1" is_animated="0" frame_rate="10">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" class="GeometryGenerator" pass="1" id="{ecce0e19-e364-4139-9352-22ad6fa58270}">
          <Option type="Map">
            <Option type="QString" value="Line" name="SymbolType"/>
            <Option type="QString" value=" segments_to_lines( $geometry )" name="geometryModifier"/>
            <Option type="QString" value="MapUnit" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol type="line" name="@1@0" force_rhr="0" alpha="1" clip_to_extent="1" is_animated="0" frame_rate="10">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" locked="0" class="ArrowLine" pass="0" id="{aa78feaf-90d0-4cfd-acd2-2f60f78103a9}">
              <Option type="Map">
                <Option type="QString" value="1" name="arrow_start_width"/>
                <Option type="QString" value="MM" name="arrow_start_width_unit"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_start_width_unit_scale"/>
                <Option type="QString" value="0" name="arrow_type"/>
                <Option type="QString" value="0" name="arrow_width"/>
                <Option type="QString" value="MM" name="arrow_width_unit"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_width_unit_scale"/>
                <Option type="QString" value="1.5" name="head_length"/>
                <Option type="QString" value="MM" name="head_length_unit"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="head_length_unit_scale"/>
                <Option type="QString" value="1.5" name="head_thickness"/>
                <Option type="QString" value="MM" name="head_thickness_unit"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="head_thickness_unit_scale"/>
                <Option type="QString" value="2" name="head_type"/>
                <Option type="QString" value="1" name="is_curved"/>
                <Option type="QString" value="1" name="is_repeated"/>
                <Option type="QString" value="-5" name="offset"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_unit_scale"/>
                <Option type="QString" value="0" name="ring_filter"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol type="fill" name="@@1@0@0" force_rhr="0" alpha="1" clip_to_extent="1" is_animated="0" frame_rate="10">
                <data_defined_properties>
                  <Option type="Map">
                    <Option type="QString" value="" name="name"/>
                    <Option name="properties"/>
                    <Option type="QString" value="collection" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer enabled="1" locked="0" class="SimpleFill" pass="0" id="{fc97198e-f6c4-4964-8c9d-6097218eae7a}">
                  <Option type="Map">
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
                    <Option type="QString" value="31,31,31,255,rgb:0.12156862745098039,0.12156862745098039,0.12156862745098039,1" name="color"/>
                    <Option type="QString" value="bevel" name="joinstyle"/>
                    <Option type="QString" value="0,0" name="offset"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                    <Option type="QString" value="MM" name="offset_unit"/>
                    <Option type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" name="outline_color"/>
                    <Option type="QString" value="solid" name="outline_style"/>
                    <Option type="QString" value="0.125" name="outline_width"/>
                    <Option type="QString" value="MM" name="outline_width_unit"/>
                    <Option type="QString" value="solid" name="style"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option type="QString" value="" name="name"/>
                      <Option name="properties"/>
                      <Option type="QString" value="collection" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
            <layer enabled="1" locked="0" class="MarkerLine" pass="0" id="{7669c563-7c94-4b99-9da0-6ec7d0daf18c}">
              <Option type="Map">
                <Option type="QString" value="4" name="average_angle_length"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="average_angle_map_unit_scale"/>
                <Option type="QString" value="MM" name="average_angle_unit"/>
                <Option type="QString" value="3" name="interval"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="interval_map_unit_scale"/>
                <Option type="QString" value="MM" name="interval_unit"/>
                <Option type="QString" value="-5" name="offset"/>
                <Option type="QString" value="0" name="offset_along_line"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_along_line_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_along_line_unit"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="bool" value="true" name="place_on_every_part"/>
                <Option type="QString" value="CentralPoint" name="placements"/>
                <Option type="QString" value="0" name="ring_filter"/>
                <Option type="QString" value="1" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol type="marker" name="@@1@0@1" force_rhr="0" alpha="1" clip_to_extent="1" is_animated="0" frame_rate="10">
                <data_defined_properties>
                  <Option type="Map">
                    <Option type="QString" value="" name="name"/>
                    <Option name="properties"/>
                    <Option type="QString" value="collection" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer enabled="1" locked="0" class="FontMarker" pass="0" id="{67addec4-7e7e-4661-8b88-6a405a52f34c}">
                  <Option type="Map">
                    <Option type="QString" value="0" name="angle"/>
                    <Option type="QString" value="A" name="chr"/>
                    <Option type="QString" value="31,31,31,255,rgb:0.12156862745098039,0.12156862745098039,0.12156862745098039,1" name="color"/>
                    <Option type="QString" value="Arial" name="font"/>
                    <Option type="QString" value="Normal" name="font_style"/>
                    <Option type="QString" value="1" name="horizontal_anchor_point"/>
                    <Option type="QString" value="bevel" name="joinstyle"/>
                    <Option type="QString" value="0,-6" name="offset"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                    <Option type="QString" value="Point" name="offset_unit"/>
                    <Option type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" name="outline_color"/>
                    <Option type="QString" value="0" name="outline_width"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale"/>
                    <Option type="QString" value="MM" name="outline_width_unit"/>
                    <Option type="QString" value="8" name="size"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="size_map_unit_scale"/>
                    <Option type="QString" value="Point" name="size_unit"/>
                    <Option type="QString" value="1" name="vertical_anchor_point"/>
                  </Option>
                  <effect enabled="1" type="effectStack">
                    <effect type="dropShadow">
                      <Option type="Map">
                        <Option type="QString" value="13" name="blend_mode"/>
                        <Option type="QString" value="2.645" name="blur_level"/>
                        <Option type="QString" value="MM" name="blur_unit"/>
                        <Option type="QString" value="3x:0,0,0,0,0,0" name="blur_unit_scale"/>
                        <Option type="QString" value="0,0,0,255,rgb:0,0,0,1" name="color"/>
                        <Option type="QString" value="2" name="draw_mode"/>
                        <Option type="QString" value="0" name="enabled"/>
                        <Option type="QString" value="135" name="offset_angle"/>
                        <Option type="QString" value="2" name="offset_distance"/>
                        <Option type="QString" value="MM" name="offset_unit"/>
                        <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_unit_scale"/>
                        <Option type="QString" value="1" name="opacity"/>
                      </Option>
                    </effect>
                    <effect type="outerGlow">
                      <Option type="Map">
                        <Option type="QString" value="0" name="blend_mode"/>
                        <Option type="QString" value="1" name="blur_level"/>
                        <Option type="QString" value="MM" name="blur_unit"/>
                        <Option type="QString" value="3x:0,0,0,0,0,0" name="blur_unit_scale"/>
                        <Option type="QString" value="69,116,40,255,rgb:0.27058823529411763,0.45490196078431372,0.15686274509803921,1" name="color1"/>
                        <Option type="QString" value="188,220,60,255,rgb:0.73725490196078436,0.86274509803921573,0.23529411764705882,1" name="color2"/>
                        <Option type="QString" value="0" name="color_type"/>
                        <Option type="QString" value="ccw" name="direction"/>
                        <Option type="QString" value="0" name="discrete"/>
                        <Option type="QString" value="2" name="draw_mode"/>
                        <Option type="QString" value="1" name="enabled"/>
                        <Option type="QString" value="0.5" name="opacity"/>
                        <Option type="QString" value="gradient" name="rampType"/>
                        <Option type="QString" value="255,255,255,255,rgb:1,1,1,1" name="single_color"/>
                        <Option type="QString" value="rgb" name="spec"/>
                        <Option type="QString" value="2.5" name="spread"/>
                        <Option type="QString" value="MM" name="spread_unit"/>
                        <Option type="QString" value="3x:0,0,0,0,0,0" name="spread_unit_scale"/>
                      </Option>
                    </effect>
                    <effect type="drawSource">
                      <Option type="Map">
                        <Option type="QString" value="0" name="blend_mode"/>
                        <Option type="QString" value="2" name="draw_mode"/>
                        <Option type="QString" value="1" name="enabled"/>
                        <Option type="QString" value="1" name="opacity"/>
                      </Option>
                    </effect>
                    <effect type="innerShadow">
                      <Option type="Map">
                        <Option type="QString" value="13" name="blend_mode"/>
                        <Option type="QString" value="2.645" name="blur_level"/>
                        <Option type="QString" value="MM" name="blur_unit"/>
                        <Option type="QString" value="3x:0,0,0,0,0,0" name="blur_unit_scale"/>
                        <Option type="QString" value="0,0,0,255,rgb:0,0,0,1" name="color"/>
                        <Option type="QString" value="2" name="draw_mode"/>
                        <Option type="QString" value="0" name="enabled"/>
                        <Option type="QString" value="135" name="offset_angle"/>
                        <Option type="QString" value="2" name="offset_distance"/>
                        <Option type="QString" value="MM" name="offset_unit"/>
                        <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_unit_scale"/>
                        <Option type="QString" value="1" name="opacity"/>
                      </Option>
                    </effect>
                    <effect type="innerGlow">
                      <Option type="Map">
                        <Option type="QString" value="0" name="blend_mode"/>
                        <Option type="QString" value="2.645" name="blur_level"/>
                        <Option type="QString" value="MM" name="blur_unit"/>
                        <Option type="QString" value="3x:0,0,0,0,0,0" name="blur_unit_scale"/>
                        <Option type="QString" value="69,116,40,255,rgb:0.27058823529411763,0.45490196078431372,0.15686274509803921,1" name="color1"/>
                        <Option type="QString" value="188,220,60,255,rgb:0.73725490196078436,0.86274509803921573,0.23529411764705882,1" name="color2"/>
                        <Option type="QString" value="0" name="color_type"/>
                        <Option type="QString" value="ccw" name="direction"/>
                        <Option type="QString" value="0" name="discrete"/>
                        <Option type="QString" value="2" name="draw_mode"/>
                        <Option type="QString" value="0" name="enabled"/>
                        <Option type="QString" value="0.5" name="opacity"/>
                        <Option type="QString" value="gradient" name="rampType"/>
                        <Option type="QString" value="255,255,255,255,rgb:1,1,1,1" name="single_color"/>
                        <Option type="QString" value="rgb" name="spec"/>
                        <Option type="QString" value="2" name="spread"/>
                        <Option type="QString" value="MM" name="spread_unit"/>
                        <Option type="QString" value="3x:0,0,0,0,0,0" name="spread_unit_scale"/>
                      </Option>
                    </effect>
                  </effect>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option type="QString" value="" name="name"/>
                      <Option type="Map" name="properties">
                        <Option type="Map" name="angle">
                          <Option type="bool" value="true" name="active"/>
                          <Option type="QString" value="if (&#xd;&#xa;degrees(  &#xd;&#xa;azimuth(&#xd;&#xa;start_point(geometry_n(  $geometry,  @geometry_part_num )), end_point(geometry_n(  $geometry,  @geometry_part_num )))) > 180, 180,0)" name="expression"/>
                          <Option type="int" value="3" name="type"/>
                        </Option>
                        <Option type="Map" name="char">
                          <Option type="bool" value="true" name="active"/>
                          <Option type="QString" value="[EXPRESSION_DISTANCE]" name="expression"/>
                          <Option type="int" value="3" name="type"/>
                        </Option>
                      </Option>
                      <Option type="QString" value="collection" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
            <layer enabled="1" locked="0" class="SimpleLine" pass="0" id="{710a335c-9c7e-41c7-b1d5-a917524cbc47}">
              <Option type="Map">
                <Option type="QString" value="0" name="align_dash_pattern"/>
                <Option type="QString" value="square" name="capstyle"/>
                <Option type="QString" value="5;2" name="customdash"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale"/>
                <Option type="QString" value="MM" name="customdash_unit"/>
                <Option type="QString" value="0" name="dash_pattern_offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="dash_pattern_offset_unit"/>
                <Option type="QString" value="0" name="draw_inside_polygon"/>
                <Option type="QString" value="bevel" name="joinstyle"/>
                <Option type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" name="line_color"/>
                <Option type="QString" value="solid" name="line_style"/>
                <Option type="QString" value="0.2" name="line_width"/>
                <Option type="QString" value="MM" name="line_width_unit"/>
                <Option type="QString" value="-5" name="offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="QString" value="0" name="ring_filter"/>
                <Option type="QString" value="0" name="trim_distance_end"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale"/>
                <Option type="QString" value="MM" name="trim_distance_end_unit"/>
                <Option type="QString" value="0" name="trim_distance_start"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale"/>
                <Option type="QString" value="MM" name="trim_distance_start_unit"/>
                <Option type="QString" value="0" name="tweak_dash_pattern_on_corners"/>
                <Option type="QString" value="0" name="use_custom_dash"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
            <layer enabled="1" locked="0" class="MarkerLine" pass="0" id="{461470f5-e05c-4659-b1a6-6d41c650160e}">
              <Option type="Map">
                <Option type="QString" value="4" name="average_angle_length"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="average_angle_map_unit_scale"/>
                <Option type="QString" value="MM" name="average_angle_unit"/>
                <Option type="QString" value="3" name="interval"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="interval_map_unit_scale"/>
                <Option type="QString" value="MM" name="interval_unit"/>
                <Option type="QString" value="-5" name="offset"/>
                <Option type="QString" value="0" name="offset_along_line"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_along_line_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_along_line_unit"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="bool" value="true" name="place_on_every_part"/>
                <Option type="QString" value="LastVertex|FirstVertex|InnerVertices" name="placements"/>
                <Option type="QString" value="0" name="ring_filter"/>
                <Option type="QString" value="1" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol type="marker" name="@@1@0@3" force_rhr="0" alpha="1" clip_to_extent="1" is_animated="0" frame_rate="10">
                <data_defined_properties>
                  <Option type="Map">
                    <Option type="QString" value="" name="name"/>
                    <Option name="properties"/>
                    <Option type="QString" value="collection" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer enabled="1" locked="0" class="SimpleMarker" pass="0" id="{db1ce3d6-58b8-4aa7-b40d-260112f0574a}">
                  <Option type="Map">
                    <Option type="QString" value="0" name="angle"/>
                    <Option type="QString" value="square" name="cap_style"/>
                    <Option type="QString" value="255,0,0,255,rgb:1,0,0,1" name="color"/>
                    <Option type="QString" value="1" name="horizontal_anchor_point"/>
                    <Option type="QString" value="bevel" name="joinstyle"/>
                    <Option type="QString" value="line" name="name"/>
                    <Option type="QString" value="0,0" name="offset"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                    <Option type="QString" value="MM" name="offset_unit"/>
                    <Option type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" name="outline_color"/>
                    <Option type="QString" value="solid" name="outline_style"/>
                    <Option type="QString" value="0.3" name="outline_width"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale"/>
                    <Option type="QString" value="MM" name="outline_width_unit"/>
                    <Option type="QString" value="diameter" name="scale_method"/>
                    <Option type="QString" value="10" name="size"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="size_map_unit_scale"/>
                    <Option type="QString" value="MM" name="size_unit"/>
                    <Option type="QString" value="1" name="vertical_anchor_point"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option type="QString" value="" name="name"/>
                      <Option name="properties"/>
                      <Option type="QString" value="collection" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol type="fill" name="2" force_rhr="0" alpha="1" clip_to_extent="1" is_animated="0" frame_rate="10">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" class="GeometryGenerator" pass="1" id="{e7893cc9-483d-4dba-bf0c-8d25d21ce6d5}">
          <Option type="Map">
            <Option type="QString" value="Line" name="SymbolType"/>
            <Option type="QString" value=" segments_to_lines( $geometry )" name="geometryModifier"/>
            <Option type="QString" value="MapUnit" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol type="line" name="@2@0" force_rhr="0" alpha="1" clip_to_extent="1" is_animated="0" frame_rate="10">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" locked="0" class="ArrowLine" pass="0" id="{0a62ca9e-132d-481c-91e4-61291c94d3cf}">
              <Option type="Map">
                <Option type="QString" value="1" name="arrow_start_width"/>
                <Option type="QString" value="MM" name="arrow_start_width_unit"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_start_width_unit_scale"/>
                <Option type="QString" value="0" name="arrow_type"/>
                <Option type="QString" value="0" name="arrow_width"/>
                <Option type="QString" value="MM" name="arrow_width_unit"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_width_unit_scale"/>
                <Option type="QString" value="1.5" name="head_length"/>
                <Option type="QString" value="MM" name="head_length_unit"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="head_length_unit_scale"/>
                <Option type="QString" value="1.5" name="head_thickness"/>
                <Option type="QString" value="MM" name="head_thickness_unit"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="head_thickness_unit_scale"/>
                <Option type="QString" value="2" name="head_type"/>
                <Option type="QString" value="1" name="is_curved"/>
                <Option type="QString" value="1" name="is_repeated"/>
                <Option type="QString" value="-5" name="offset"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_unit_scale"/>
                <Option type="QString" value="0" name="ring_filter"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol type="fill" name="@@2@0@0" force_rhr="0" alpha="1" clip_to_extent="1" is_animated="0" frame_rate="10">
                <data_defined_properties>
                  <Option type="Map">
                    <Option type="QString" value="" name="name"/>
                    <Option name="properties"/>
                    <Option type="QString" value="collection" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer enabled="1" locked="0" class="SimpleFill" pass="0" id="{acb78264-31e3-4e78-acbc-e4e41fae7da0}">
                  <Option type="Map">
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
                    <Option type="QString" value="31,31,31,255,rgb:0.12156862745098039,0.12156862745098039,0.12156862745098039,1" name="color"/>
                    <Option type="QString" value="bevel" name="joinstyle"/>
                    <Option type="QString" value="0,0" name="offset"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                    <Option type="QString" value="MM" name="offset_unit"/>
                    <Option type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" name="outline_color"/>
                    <Option type="QString" value="solid" name="outline_style"/>
                    <Option type="QString" value="0.125" name="outline_width"/>
                    <Option type="QString" value="MM" name="outline_width_unit"/>
                    <Option type="QString" value="solid" name="style"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option type="QString" value="" name="name"/>
                      <Option name="properties"/>
                      <Option type="QString" value="collection" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
            <layer enabled="1" locked="0" class="MarkerLine" pass="0" id="{acb59461-508b-4c6e-b8f1-983941a2cc25}">
              <Option type="Map">
                <Option type="QString" value="4" name="average_angle_length"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="average_angle_map_unit_scale"/>
                <Option type="QString" value="MM" name="average_angle_unit"/>
                <Option type="QString" value="3" name="interval"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="interval_map_unit_scale"/>
                <Option type="QString" value="MM" name="interval_unit"/>
                <Option type="QString" value="-5" name="offset"/>
                <Option type="QString" value="0" name="offset_along_line"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_along_line_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_along_line_unit"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="bool" value="true" name="place_on_every_part"/>
                <Option type="QString" value="CentralPoint" name="placements"/>
                <Option type="QString" value="0" name="ring_filter"/>
                <Option type="QString" value="1" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol type="marker" name="@@2@0@1" force_rhr="0" alpha="1" clip_to_extent="1" is_animated="0" frame_rate="10">
                <data_defined_properties>
                  <Option type="Map">
                    <Option type="QString" value="" name="name"/>
                    <Option name="properties"/>
                    <Option type="QString" value="collection" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer enabled="1" locked="0" class="FontMarker" pass="0" id="{46cc8ff9-7fa6-43e1-8af3-27ca8eab6b36}">
                  <Option type="Map">
                    <Option type="QString" value="0" name="angle"/>
                    <Option type="QString" value="A" name="chr"/>
                    <Option type="QString" value="31,31,31,255,rgb:0.12156862745098039,0.12156862745098039,0.12156862745098039,1" name="color"/>
                    <Option type="QString" value="Arial" name="font"/>
                    <Option type="QString" value="Normal" name="font_style"/>
                    <Option type="QString" value="1" name="horizontal_anchor_point"/>
                    <Option type="QString" value="bevel" name="joinstyle"/>
                    <Option type="QString" value="0,5" name="offset"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                    <Option type="QString" value="Point" name="offset_unit"/>
                    <Option type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" name="outline_color"/>
                    <Option type="QString" value="0" name="outline_width"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale"/>
                    <Option type="QString" value="MM" name="outline_width_unit"/>
                    <Option type="QString" value="8" name="size"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="size_map_unit_scale"/>
                    <Option type="QString" value="Point" name="size_unit"/>
                    <Option type="QString" value="1" name="vertical_anchor_point"/>
                  </Option>
                  <effect enabled="1" type="effectStack">
                    <effect type="dropShadow">
                      <Option type="Map">
                        <Option type="QString" value="13" name="blend_mode"/>
                        <Option type="QString" value="2.645" name="blur_level"/>
                        <Option type="QString" value="MM" name="blur_unit"/>
                        <Option type="QString" value="3x:0,0,0,0,0,0" name="blur_unit_scale"/>
                        <Option type="QString" value="0,0,0,255,rgb:0,0,0,1" name="color"/>
                        <Option type="QString" value="2" name="draw_mode"/>
                        <Option type="QString" value="0" name="enabled"/>
                        <Option type="QString" value="135" name="offset_angle"/>
                        <Option type="QString" value="2" name="offset_distance"/>
                        <Option type="QString" value="MM" name="offset_unit"/>
                        <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_unit_scale"/>
                        <Option type="QString" value="1" name="opacity"/>
                      </Option>
                    </effect>
                    <effect type="outerGlow">
                      <Option type="Map">
                        <Option type="QString" value="0" name="blend_mode"/>
                        <Option type="QString" value="1" name="blur_level"/>
                        <Option type="QString" value="MM" name="blur_unit"/>
                        <Option type="QString" value="3x:0,0,0,0,0,0" name="blur_unit_scale"/>
                        <Option type="QString" value="69,116,40,255,rgb:0.27058823529411763,0.45490196078431372,0.15686274509803921,1" name="color1"/>
                        <Option type="QString" value="188,220,60,255,rgb:0.73725490196078436,0.86274509803921573,0.23529411764705882,1" name="color2"/>
                        <Option type="QString" value="0" name="color_type"/>
                        <Option type="QString" value="ccw" name="direction"/>
                        <Option type="QString" value="0" name="discrete"/>
                        <Option type="QString" value="2" name="draw_mode"/>
                        <Option type="QString" value="1" name="enabled"/>
                        <Option type="QString" value="0.5" name="opacity"/>
                        <Option type="QString" value="gradient" name="rampType"/>
                        <Option type="QString" value="255,255,255,255,rgb:1,1,1,1" name="single_color"/>
                        <Option type="QString" value="rgb" name="spec"/>
                        <Option type="QString" value="3" name="spread"/>
                        <Option type="QString" value="MM" name="spread_unit"/>
                        <Option type="QString" value="3x:0,0,0,0,0,0" name="spread_unit_scale"/>
                      </Option>
                    </effect>
                    <effect type="drawSource">
                      <Option type="Map">
                        <Option type="QString" value="0" name="blend_mode"/>
                        <Option type="QString" value="2" name="draw_mode"/>
                        <Option type="QString" value="1" name="enabled"/>
                        <Option type="QString" value="1" name="opacity"/>
                      </Option>
                    </effect>
                    <effect type="innerShadow">
                      <Option type="Map">
                        <Option type="QString" value="13" name="blend_mode"/>
                        <Option type="QString" value="2.645" name="blur_level"/>
                        <Option type="QString" value="MM" name="blur_unit"/>
                        <Option type="QString" value="3x:0,0,0,0,0,0" name="blur_unit_scale"/>
                        <Option type="QString" value="0,0,0,255,rgb:0,0,0,1" name="color"/>
                        <Option type="QString" value="2" name="draw_mode"/>
                        <Option type="QString" value="0" name="enabled"/>
                        <Option type="QString" value="135" name="offset_angle"/>
                        <Option type="QString" value="2" name="offset_distance"/>
                        <Option type="QString" value="MM" name="offset_unit"/>
                        <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_unit_scale"/>
                        <Option type="QString" value="1" name="opacity"/>
                      </Option>
                    </effect>
                    <effect type="innerGlow">
                      <Option type="Map">
                        <Option type="QString" value="0" name="blend_mode"/>
                        <Option type="QString" value="2.645" name="blur_level"/>
                        <Option type="QString" value="MM" name="blur_unit"/>
                        <Option type="QString" value="3x:0,0,0,0,0,0" name="blur_unit_scale"/>
                        <Option type="QString" value="69,116,40,255,rgb:0.27058823529411763,0.45490196078431372,0.15686274509803921,1" name="color1"/>
                        <Option type="QString" value="188,220,60,255,rgb:0.73725490196078436,0.86274509803921573,0.23529411764705882,1" name="color2"/>
                        <Option type="QString" value="0" name="color_type"/>
                        <Option type="QString" value="ccw" name="direction"/>
                        <Option type="QString" value="0" name="discrete"/>
                        <Option type="QString" value="2" name="draw_mode"/>
                        <Option type="QString" value="0" name="enabled"/>
                        <Option type="QString" value="0.5" name="opacity"/>
                        <Option type="QString" value="gradient" name="rampType"/>
                        <Option type="QString" value="255,255,255,255,rgb:1,1,1,1" name="single_color"/>
                        <Option type="QString" value="rgb" name="spec"/>
                        <Option type="QString" value="2" name="spread"/>
                        <Option type="QString" value="MM" name="spread_unit"/>
                        <Option type="QString" value="3x:0,0,0,0,0,0" name="spread_unit_scale"/>
                      </Option>
                    </effect>
                  </effect>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option type="QString" value="" name="name"/>
                      <Option type="Map" name="properties">
                        <Option type="Map" name="angle">
                          <Option type="bool" value="true" name="active"/>
                          <Option type="QString" value="if ( degrees( azimuth(start_point(geometry_n(  $geometry,  @geometry_part_num )), end_point(geometry_n(  $geometry,  @geometry_part_num )))) > 180, 180,0)" name="expression"/>
                          <Option type="int" value="3" name="type"/>
                        </Option>
                        <Option type="Map" name="char">
                          <Option type="bool" value="true" name="active"/>
                          <Option type="QString" value="[EXPRESSION_AZIMUTH]" name="expression"/>
                          <Option type="int" value="3" name="type"/>
                        </Option>
                      </Option>
                      <Option type="QString" value="collection" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
            <layer enabled="1" locked="0" class="SimpleLine" pass="0" id="{981ae034-6476-433f-b131-54ba591d7bf5}">
              <Option type="Map">
                <Option type="QString" value="0" name="align_dash_pattern"/>
                <Option type="QString" value="square" name="capstyle"/>
                <Option type="QString" value="5;2" name="customdash"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale"/>
                <Option type="QString" value="MM" name="customdash_unit"/>
                <Option type="QString" value="0" name="dash_pattern_offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="dash_pattern_offset_unit"/>
                <Option type="QString" value="0" name="draw_inside_polygon"/>
                <Option type="QString" value="bevel" name="joinstyle"/>
                <Option type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" name="line_color"/>
                <Option type="QString" value="solid" name="line_style"/>
                <Option type="QString" value="0.2" name="line_width"/>
                <Option type="QString" value="MM" name="line_width_unit"/>
                <Option type="QString" value="-5" name="offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="QString" value="0" name="ring_filter"/>
                <Option type="QString" value="0" name="trim_distance_end"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale"/>
                <Option type="QString" value="MM" name="trim_distance_end_unit"/>
                <Option type="QString" value="0" name="trim_distance_start"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale"/>
                <Option type="QString" value="MM" name="trim_distance_start_unit"/>
                <Option type="QString" value="0" name="tweak_dash_pattern_on_corners"/>
                <Option type="QString" value="0" name="use_custom_dash"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
            <layer enabled="1" locked="0" class="MarkerLine" pass="0" id="{003b12cc-894f-44b2-860c-7b6ca8edc7ec}">
              <Option type="Map">
                <Option type="QString" value="4" name="average_angle_length"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="average_angle_map_unit_scale"/>
                <Option type="QString" value="MM" name="average_angle_unit"/>
                <Option type="QString" value="3" name="interval"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="interval_map_unit_scale"/>
                <Option type="QString" value="MM" name="interval_unit"/>
                <Option type="QString" value="-5" name="offset"/>
                <Option type="QString" value="0" name="offset_along_line"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_along_line_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_along_line_unit"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="bool" value="true" name="place_on_every_part"/>
                <Option type="QString" value="LastVertex|FirstVertex|InnerVertices" name="placements"/>
                <Option type="QString" value="0" name="ring_filter"/>
                <Option type="QString" value="1" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol type="marker" name="@@2@0@3" force_rhr="0" alpha="1" clip_to_extent="1" is_animated="0" frame_rate="10">
                <data_defined_properties>
                  <Option type="Map">
                    <Option type="QString" value="" name="name"/>
                    <Option name="properties"/>
                    <Option type="QString" value="collection" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer enabled="1" locked="0" class="SimpleMarker" pass="0" id="{11797569-c7da-43da-9e8f-631e13b4848b}">
                  <Option type="Map">
                    <Option type="QString" value="0" name="angle"/>
                    <Option type="QString" value="square" name="cap_style"/>
                    <Option type="QString" value="255,0,0,255,rgb:1,0,0,1" name="color"/>
                    <Option type="QString" value="1" name="horizontal_anchor_point"/>
                    <Option type="QString" value="bevel" name="joinstyle"/>
                    <Option type="QString" value="line" name="name"/>
                    <Option type="QString" value="0,0" name="offset"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                    <Option type="QString" value="MM" name="offset_unit"/>
                    <Option type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" name="outline_color"/>
                    <Option type="QString" value="solid" name="outline_style"/>
                    <Option type="QString" value="0.3" name="outline_width"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale"/>
                    <Option type="QString" value="MM" name="outline_width_unit"/>
                    <Option type="QString" value="diameter" name="scale_method"/>
                    <Option type="QString" value="10" name="size"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="size_map_unit_scale"/>
                    <Option type="QString" value="MM" name="size_unit"/>
                    <Option type="QString" value="1" name="vertical_anchor_point"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option type="QString" value="" name="name"/>
                      <Option name="properties"/>
                      <Option type="QString" value="collection" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol type="fill" name="3" force_rhr="0" alpha="1" clip_to_extent="1" is_animated="0" frame_rate="10">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" class="SimpleFill" pass="0" id="{2026613e-1711-4cdd-8c7f-6dec1ba715de}">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="235,176,121,111,rgb:0.92156862745098034,0.69019607843137254,0.47450980392156861,0.43529411764705883" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.43" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="solid" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <data-defined-properties>
      <Option type="Map">
        <Option type="QString" value="" name="name"/>
        <Option name="properties"/>
        <Option type="QString" value="collection" name="type"/>
      </Option>
    </data-defined-properties>
  </renderer-v2>
  <selection mode="Default">
    <selectionColor invalid="1"/>
    <selectionSymbol>
      <symbol type="fill" name="" force_rhr="0" alpha="1" clip_to_extent="1" is_animated="0" frame_rate="10">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" class="SimpleFill" pass="0" id="{3a33b687-2566-4f6e-8655-367e78a26c3e}">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="0,0,255,255,rgb:0,0,1,1" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="solid" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </selectionSymbol>
  </selection>
  <labeling type="rule-based">
    <rules key="{74854f65-9f49-4ae6-a72d-ae437a94fbd5}">
      <rule key="{1903eeec-b4f0-4b01-877c-27d327f41a30}">
        <settings calloutType="simple">
          <text-style tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" namedStyle="Normal" fontKerning="1" fontFamily="MS Shell Dlg 2" fontLetterSpacing="0" isExpression="1" fontStrikeout="0" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" legendString="Aa" multilineHeightUnit="Percentage" allowHtml="0" fontSizeUnit="Point" fontUnderline="0" forcedBold="0" textColor="255,255,255,255,rgb:1,1,1,1" tabStopDistanceUnit="Point" fontItalic="0" fieldName="[EXPRESSION_AREA]" fontWordSpacing="0" multilineHeight="1" blendMode="0" useSubstitutions="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontWeight="50" forcedItalic="0" capitalization="0" fontSize="12" textOpacity="1" tabStopDistance="80" textOrientation="horizontal">
            <families/>
            <text-buffer bufferSizeUnits="MM" bufferNoFill="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferBlendMode="0" bufferDraw="1" bufferSize="0.5" bufferColor="31,31,31,255,rgb:0.12156862745098039,0.12156862745098039,0.12156862745098039,1" bufferOpacity="0.48100000000000004" bufferJoinStyle="128">
              <effect enabled="1" type="effectStack">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option type="QString" value="13" name="blend_mode"/>
                    <Option type="QString" value="2.645" name="blur_level"/>
                    <Option type="QString" value="MM" name="blur_unit"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="blur_unit_scale"/>
                    <Option type="QString" value="0,0,0,255,rgb:0,0,0,1" name="color"/>
                    <Option type="QString" value="2" name="draw_mode"/>
                    <Option type="QString" value="0" name="enabled"/>
                    <Option type="QString" value="135" name="offset_angle"/>
                    <Option type="QString" value="2" name="offset_distance"/>
                    <Option type="QString" value="MM" name="offset_unit"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_unit_scale"/>
                    <Option type="QString" value="1" name="opacity"/>
                  </Option>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option type="QString" value="0" name="blend_mode"/>
                    <Option type="QString" value="1" name="blur_level"/>
                    <Option type="QString" value="MM" name="blur_unit"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="blur_unit_scale"/>
                    <Option type="QString" value="48,18,59,255,rgb:0.18823529411764706,0.07058823529411765,0.23137254901960785,1" name="color1"/>
                    <Option type="QString" value="122,4,3,255,rgb:0.47843137254901963,0.01568627450980392,0.01176470588235294,1" name="color2"/>
                    <Option type="QString" value="1" name="color_type"/>
                    <Option type="QString" value="ccw" name="direction"/>
                    <Option type="QString" value="0" name="discrete"/>
                    <Option type="QString" value="2" name="draw_mode"/>
                    <Option type="QString" value="1" name="enabled"/>
                    <Option type="QString" value="0.5" name="opacity"/>
                    <Option type="QString" value="gradient" name="rampType"/>
                    <Option type="QString" value="255,255,255,255,rgb:1,1,1,1" name="single_color"/>
                    <Option type="QString" value="rgb" name="spec"/>
                    <Option type="QString" value="3" name="spread"/>
                    <Option type="QString" value="MM" name="spread_unit"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="spread_unit_scale"/>
                    <Option type="QString" value="0.0039063;50,21,67,255,rgb:0.19607843137254902,0.08235294117647059,0.2627450980392157,1;rgb;ccw:0.0078125;51,24,74,255,rgb:0.20000000000000001,0.09411764705882353,0.29019607843137257,1;rgb;ccw:0.0117188;52,27,81,255,rgb:0.20392156862745098,0.10588235294117647,0.31764705882352939,1;rgb;ccw:0.015625;53,30,88,255,rgb:0.20784313725490197,0.11764705882352941,0.34509803921568627,1;rgb;ccw:0.0195313;54,33,95,255,rgb:0.21176470588235294,0.12941176470588237,0.37254901960784315,1;rgb;ccw:0.0234375;55,36,102,255,rgb:0.21568627450980393,0.14117647058823529,0.40000000000000002,1;rgb;ccw:0.0273438;56,39,109,255,rgb:0.2196078431372549,0.15294117647058825,0.42745098039215684,1;rgb;ccw:0.03125;57,42,115,255,rgb:0.22352941176470589,0.16470588235294117,0.45098039215686275,1;rgb;ccw:0.0351563;58,45,121,255,rgb:0.22745098039215686,0.17647058823529413,0.47450980392156861,1;rgb;ccw:0.0390625;59,47,128,255,rgb:0.23137254901960785,0.18431372549019609,0.50196078431372548,1;rgb;ccw:0.0429688;60,50,134,255,rgb:0.23529411764705882,0.19607843137254902,0.52549019607843139,1;rgb;ccw:0.046875;61,53,139,255,rgb:0.23921568627450981,0.20784313725490197,0.54509803921568623,1;rgb;ccw:0.0507813;62,56,145,255,rgb:0.24313725490196078,0.2196078431372549,0.56862745098039214,1;rgb;ccw:0.0546875;63,59,151,255,rgb:0.24705882352941178,0.23137254901960785,0.59215686274509804,1;rgb;ccw:0.0585938;63,62,156,255,rgb:0.24705882352941178,0.24313725490196078,0.61176470588235299,1;rgb;ccw:0.0625;64,64,162,255,rgb:0.25098039215686274,0.25098039215686274,0.63529411764705879,1;rgb;ccw:0.0664063;65,67,167,255,rgb:0.25490196078431371,0.2627450980392157,0.65490196078431373,1;rgb;ccw:0.0703125;65,70,172,255,rgb:0.25490196078431371,0.27450980392156865,0.67450980392156867,1;rgb;ccw:0.0742188;66,73,177,255,rgb:0.25882352941176473,0.28627450980392155,0.69411764705882351,1;rgb;ccw:0.078125;66,75,181,255,rgb:0.25882352941176473,0.29411764705882354,0.70980392156862748,1;rgb;ccw:0.0820313;67,78,186,255,rgb:0.2627450980392157,0.30588235294117649,0.72941176470588232,1;rgb;ccw:0.0859375;68,81,191,255,rgb:0.26666666666666666,0.31764705882352939,0.74901960784313726,1;rgb;ccw:0.0898438;68,84,195,255,rgb:0.26666666666666666,0.32941176470588235,0.76470588235294112,1;rgb;ccw:0.09375;68,86,199,255,rgb:0.26666666666666666,0.33725490196078434,0.7803921568627451,1;rgb;ccw:0.0976563;69,89,203,255,rgb:0.27058823529411763,0.34901960784313724,0.79607843137254897,1;rgb;ccw:0.101563;69,92,207,255,rgb:0.27058823529411763,0.36078431372549019,0.81176470588235294,1;rgb;ccw:0.105469;69,94,211,255,rgb:0.27058823529411763,0.36862745098039218,0.82745098039215681,1;rgb;ccw:0.109375;70,97,214,255,rgb:0.27450980392156865,0.38039215686274508,0.83921568627450982,1;rgb;ccw:0.113281;70,100,218,255,rgb:0.27450980392156865,0.39215686274509803,0.85490196078431369,1;rgb;ccw:0.117188;70,102,221,255,rgb:0.27450980392156865,0.40000000000000002,0.8666666666666667,1;rgb;ccw:0.121094;70,105,224,255,rgb:0.27450980392156865,0.41176470588235292,0.8784313725490196,1;rgb;ccw:0.125;70,107,227,255,rgb:0.27450980392156865,0.41960784313725491,0.8901960784313725,1;rgb;ccw:0.128906;71,110,230,255,rgb:0.27843137254901962,0.43137254901960786,0.90196078431372551,1;rgb;ccw:0.132813;71,113,233,255,rgb:0.27843137254901962,0.44313725490196076,0.9137254901960784,1;rgb;ccw:0.136719;71,115,235,255,rgb:0.27843137254901962,0.45098039215686275,0.92156862745098034,1;rgb;ccw:0.140625;71,118,238,255,rgb:0.27843137254901962,0.46274509803921571,0.93333333333333335,1;rgb;ccw:0.144531;71,120,240,255,rgb:0.27843137254901962,0.47058823529411764,0.94117647058823528,1;rgb;ccw:0.148438;71,123,242,255,rgb:0.27843137254901962,0.4823529411764706,0.94901960784313721,1;rgb;ccw:0.152344;70,125,244,255,rgb:0.27450980392156865,0.49019607843137253,0.95686274509803926,1;rgb;ccw:0.15625;70,128,246,255,rgb:0.27450980392156865,0.50196078431372548,0.96470588235294119,1;rgb;ccw:0.160156;70,130,248,255,rgb:0.27450980392156865,0.50980392156862742,0.97254901960784312,1;rgb;ccw:0.164063;70,133,250,255,rgb:0.27450980392156865,0.52156862745098043,0.98039215686274506,1;rgb;ccw:0.167969;70,135,251,255,rgb:0.27450980392156865,0.52941176470588236,0.98431372549019602,1;rgb;ccw:0.171875;69,138,252,255,rgb:0.27058823529411763,0.54117647058823526,0.9882352941176471,1;rgb;ccw:0.175781;69,140,253,255,rgb:0.27058823529411763,0.5490196078431373,0.99215686274509807,1;rgb;ccw:0.179688;68,143,254,255,rgb:0.26666666666666666,0.5607843137254902,0.99607843137254903,1;rgb;ccw:0.183594;67,145,254,255,rgb:0.2627450980392157,0.56862745098039214,0.99607843137254903,1;rgb;ccw:0.1875;66,148,255,255,rgb:0.25882352941176473,0.58039215686274515,1,1;rgb;ccw:0.191406;65,150,255,255,rgb:0.25490196078431371,0.58823529411764708,1,1;rgb;ccw:0.195313;64,153,255,255,rgb:0.25098039215686274,0.59999999999999998,1,1;rgb;ccw:0.199219;62,155,254,255,rgb:0.24313725490196078,0.60784313725490191,0.99607843137254903,1;rgb;ccw:0.203125;61,158,254,255,rgb:0.23921568627450981,0.61960784313725492,0.99607843137254903,1;rgb;ccw:0.207031;59,160,253,255,rgb:0.23137254901960785,0.62745098039215685,0.99215686274509807,1;rgb;ccw:0.210938;58,163,252,255,rgb:0.22745098039215686,0.63921568627450975,0.9882352941176471,1;rgb;ccw:0.214844;56,165,251,255,rgb:0.2196078431372549,0.6470588235294118,0.98431372549019602,1;rgb;ccw:0.21875;55,168,250,255,rgb:0.21568627450980393,0.6588235294117647,0.98039215686274506,1;rgb;ccw:0.222656;53,171,248,255,rgb:0.20784313725490197,0.6705882352941176,0.97254901960784312,1;rgb;ccw:0.226563;51,173,247,255,rgb:0.20000000000000001,0.67843137254901964,0.96862745098039216,1;rgb;ccw:0.230469;49,175,245,255,rgb:0.19215686274509805,0.68627450980392157,0.96078431372549022,1;rgb;ccw:0.234375;47,178,244,255,rgb:0.18431372549019609,0.69803921568627447,0.95686274509803926,1;rgb;ccw:0.238281;46,180,242,255,rgb:0.1803921568627451,0.70588235294117652,0.94901960784313721,1;rgb;ccw:0.242188;44,183,240,255,rgb:0.17254901960784313,0.71764705882352942,0.94117647058823528,1;rgb;ccw:0.246094;42,185,238,255,rgb:0.16470588235294117,0.72549019607843135,0.93333333333333335,1;rgb;ccw:0.25;40,188,235,255,rgb:0.15686274509803921,0.73725490196078436,0.92156862745098034,1;rgb;ccw:0.253906;39,190,233,255,rgb:0.15294117647058825,0.74509803921568629,0.9137254901960784,1;rgb;ccw:0.257813;37,192,231,255,rgb:0.14509803921568629,0.75294117647058822,0.90588235294117647,1;rgb;ccw:0.261719;35,195,228,255,rgb:0.13725490196078433,0.76470588235294112,0.89411764705882357,1;rgb;ccw:0.265625;34,197,226,255,rgb:0.13333333333333333,0.77254901960784317,0.88627450980392153,1;rgb;ccw:0.269531;32,199,223,255,rgb:0.12549019607843137,0.7803921568627451,0.87450980392156863,1;rgb;ccw:0.273438;31,201,221,255,rgb:0.12156862745098039,0.78823529411764703,0.8666666666666667,1;rgb;ccw:0.277344;30,203,218,255,rgb:0.11764705882352941,0.79607843137254897,0.85490196078431369,1;rgb;ccw:0.28125;28,205,216,255,rgb:0.10980392156862745,0.80392156862745101,0.84705882352941175,1;rgb;ccw:0.285156;27,208,213,255,rgb:0.10588235294117647,0.81568627450980391,0.83529411764705885,1;rgb;ccw:0.289063;26,210,210,255,rgb:0.10196078431372549,0.82352941176470584,0.82352941176470584,1;rgb;ccw:0.292969;26,212,208,255,rgb:0.10196078431372549,0.83137254901960789,0.81568627450980391,1;rgb;ccw:0.296875;25,213,205,255,rgb:0.09803921568627451,0.83529411764705885,0.80392156862745101,1;rgb;ccw:0.300781;24,215,202,255,rgb:0.09411764705882353,0.84313725490196079,0.792156862745098,1;rgb;ccw:0.304688;24,217,200,255,rgb:0.09411764705882353,0.85098039215686272,0.78431372549019607,1;rgb;ccw:0.308594;24,219,197,255,rgb:0.09411764705882353,0.85882352941176465,0.77254901960784317,1;rgb;ccw:0.3125;24,221,194,255,rgb:0.09411764705882353,0.8666666666666667,0.76078431372549016,1;rgb;ccw:0.316406;24,222,192,255,rgb:0.09411764705882353,0.87058823529411766,0.75294117647058822,1;rgb;ccw:0.320313;24,224,189,255,rgb:0.09411764705882353,0.8784313725490196,0.74117647058823533,1;rgb;ccw:0.324219;25,226,187,255,rgb:0.09803921568627451,0.88627450980392153,0.73333333333333328,1;rgb;ccw:0.328125;25,227,185,255,rgb:0.09803921568627451,0.8901960784313725,0.72549019607843135,1;rgb;ccw:0.332031;26,228,182,255,rgb:0.10196078431372549,0.89411764705882357,0.71372549019607845,1;rgb;ccw:0.335938;28,230,180,255,rgb:0.10980392156862745,0.90196078431372551,0.70588235294117652,1;rgb;ccw:0.339844;29,231,178,255,rgb:0.11372549019607843,0.90588235294117647,0.69803921568627447,1;rgb;ccw:0.34375;31,233,175,255,rgb:0.12156862745098039,0.9137254901960784,0.68627450980392157,1;rgb;ccw:0.347656;32,234,172,255,rgb:0.12549019607843137,0.91764705882352937,0.67450980392156867,1;rgb;ccw:0.351563;34,235,170,255,rgb:0.13333333333333333,0.92156862745098034,0.66666666666666663,1;rgb;ccw:0.355469;37,236,167,255,rgb:0.14509803921568629,0.92549019607843142,0.65490196078431373,1;rgb;ccw:0.359375;39,238,164,255,rgb:0.15294117647058825,0.93333333333333335,0.64313725490196083,1;rgb;ccw:0.363281;42,239,161,255,rgb:0.16470588235294117,0.93725490196078431,0.63137254901960782,1;rgb;ccw:0.367188;44,240,158,255,rgb:0.17254901960784313,0.94117647058823528,0.61960784313725492,1;rgb;ccw:0.371094;47,241,155,255,rgb:0.18431372549019609,0.94509803921568625,0.60784313725490191,1;rgb;ccw:0.375;50,242,152,255,rgb:0.19607843137254902,0.94901960784313721,0.59607843137254901,1;rgb;ccw:0.378906;53,243,148,255,rgb:0.20784313725490197,0.95294117647058818,0.58039215686274515,1;rgb;ccw:0.382813;56,244,145,255,rgb:0.2196078431372549,0.95686274509803926,0.56862745098039214,1;rgb;ccw:0.386719;60,245,142,255,rgb:0.23529411764705882,0.96078431372549022,0.55686274509803924,1;rgb;ccw:0.390625;63,246,138,255,rgb:0.24705882352941178,0.96470588235294119,0.54117647058823526,1;rgb;ccw:0.394531;67,247,135,255,rgb:0.2627450980392157,0.96862745098039216,0.52941176470588236,1;rgb;ccw:0.398438;70,248,132,255,rgb:0.27450980392156865,0.97254901960784312,0.51764705882352946,1;rgb;ccw:0.402344;74,248,128,255,rgb:0.29019607843137257,0.97254901960784312,0.50196078431372548,1;rgb;ccw:0.40625;78,249,125,255,rgb:0.30588235294117649,0.97647058823529409,0.49019607843137253,1;rgb;ccw:0.410156;82,250,122,255,rgb:0.32156862745098042,0.98039215686274506,0.47843137254901963,1;rgb;ccw:0.414063;85,250,118,255,rgb:0.33333333333333331,0.98039215686274506,0.46274509803921571,1;rgb;ccw:0.417969;89,251,115,255,rgb:0.34901960784313724,0.98431372549019602,0.45098039215686275,1;rgb;ccw:0.421875;93,252,111,255,rgb:0.36470588235294116,0.9882352941176471,0.43529411764705883,1;rgb;ccw:0.425781;97,252,108,255,rgb:0.38039215686274508,0.9882352941176471,0.42352941176470588,1;rgb;ccw:0.429688;101,253,105,255,rgb:0.396078431372549,0.99215686274509807,0.41176470588235292,1;rgb;ccw:0.433594;105,253,102,255,rgb:0.41176470588235292,0.99215686274509807,0.40000000000000002,1;rgb;ccw:0.4375;109,254,98,255,rgb:0.42745098039215684,0.99607843137254903,0.3843137254901961,1;rgb;ccw:0.441406;113,254,95,255,rgb:0.44313725490196076,0.99607843137254903,0.37254901960784315,1;rgb;ccw:0.445313;117,254,92,255,rgb:0.45882352941176469,0.99607843137254903,0.36078431372549019,1;rgb;ccw:0.449219;121,254,89,255,rgb:0.47450980392156861,0.99607843137254903,0.34901960784313724,1;rgb;ccw:0.453125;125,255,86,255,rgb:0.49019607843137253,1,0.33725490196078434,1;rgb;ccw:0.457031;128,255,83,255,rgb:0.50196078431372548,1,0.32549019607843138,1;rgb;ccw:0.460938;132,255,81,255,rgb:0.51764705882352946,1,0.31764705882352939,1;rgb;ccw:0.464844;136,255,78,255,rgb:0.53333333333333333,1,0.30588235294117649,1;rgb;ccw:0.46875;139,255,75,255,rgb:0.54509803921568623,1,0.29411764705882354,1;rgb;ccw:0.472656;143,255,73,255,rgb:0.5607843137254902,1,0.28627450980392155,1;rgb;ccw:0.476563;146,255,71,255,rgb:0.5725490196078431,1,0.27843137254901962,1;rgb;ccw:0.480469;150,254,68,255,rgb:0.58823529411764708,0.99607843137254903,0.26666666666666666,1;rgb;ccw:0.484375;153,254,66,255,rgb:0.59999999999999998,0.99607843137254903,0.25882352941176473,1;rgb;ccw:0.488281;156,254,64,255,rgb:0.61176470588235299,0.99607843137254903,0.25098039215686274,1;rgb;ccw:0.492188;159,253,63,255,rgb:0.62352941176470589,0.99215686274509807,0.24705882352941178,1;rgb;ccw:0.496094;161,253,61,255,rgb:0.63137254901960782,0.99215686274509807,0.23921568627450981,1;rgb;ccw:0.5;164,252,60,255,rgb:0.64313725490196083,0.9882352941176471,0.23529411764705882,1;rgb;ccw:0.503906;167,252,58,255,rgb:0.65490196078431373,0.9882352941176471,0.22745098039215686,1;rgb;ccw:0.507813;169,251,57,255,rgb:0.66274509803921566,0.98431372549019602,0.22352941176470589,1;rgb;ccw:0.511719;172,251,56,255,rgb:0.67450980392156867,0.98431372549019602,0.2196078431372549,1;rgb;ccw:0.515625;175,250,55,255,rgb:0.68627450980392157,0.98039215686274506,0.21568627450980393,1;rgb;ccw:0.519531;177,249,54,255,rgb:0.69411764705882351,0.97647058823529409,0.21176470588235294,1;rgb;ccw:0.523438;180,248,54,255,rgb:0.70588235294117652,0.97254901960784312,0.21176470588235294,1;rgb;ccw:0.527344;183,247,53,255,rgb:0.71764705882352942,0.96862745098039216,0.20784313725490197,1;rgb;ccw:0.53125;185,246,53,255,rgb:0.72549019607843135,0.96470588235294119,0.20784313725490197,1;rgb;ccw:0.535156;188,245,52,255,rgb:0.73725490196078436,0.96078431372549022,0.20392156862745098,1;rgb;ccw:0.539063;190,244,52,255,rgb:0.74509803921568629,0.95686274509803926,0.20392156862745098,1;rgb;ccw:0.542969;193,243,52,255,rgb:0.75686274509803919,0.95294117647058818,0.20392156862745098,1;rgb;ccw:0.546875;195,241,52,255,rgb:0.76470588235294112,0.94509803921568625,0.20392156862745098,1;rgb;ccw:0.550781;198,240,52,255,rgb:0.77647058823529413,0.94117647058823528,0.20392156862745098,1;rgb;ccw:0.554688;200,239,52,255,rgb:0.78431372549019607,0.93725490196078431,0.20392156862745098,1;rgb;ccw:0.558594;203,237,52,255,rgb:0.79607843137254897,0.92941176470588238,0.20392156862745098,1;rgb;ccw:0.5625;205,236,52,255,rgb:0.80392156862745101,0.92549019607843142,0.20392156862745098,1;rgb;ccw:0.566406;208,234,52,255,rgb:0.81568627450980391,0.91764705882352937,0.20392156862745098,1;rgb;ccw:0.570313;210,233,53,255,rgb:0.82352941176470584,0.9137254901960784,0.20784313725490197,1;rgb;ccw:0.574219;212,231,53,255,rgb:0.83137254901960789,0.90588235294117647,0.20784313725490197,1;rgb;ccw:0.578125;215,229,53,255,rgb:0.84313725490196079,0.89803921568627454,0.20784313725490197,1;rgb;ccw:0.582031;217,228,54,255,rgb:0.85098039215686272,0.89411764705882357,0.21176470588235294,1;rgb;ccw:0.585938;219,226,54,255,rgb:0.85882352941176465,0.88627450980392153,0.21176470588235294,1;rgb;ccw:0.589844;221,224,55,255,rgb:0.8666666666666667,0.8784313725490196,0.21568627450980393,1;rgb;ccw:0.59375;223,223,55,255,rgb:0.87450980392156863,0.87450980392156863,0.21568627450980393,1;rgb;ccw:0.597656;225,221,55,255,rgb:0.88235294117647056,0.8666666666666667,0.21568627450980393,1;rgb;ccw:0.601563;227,219,56,255,rgb:0.8901960784313725,0.85882352941176465,0.2196078431372549,1;rgb;ccw:0.605469;229,217,56,255,rgb:0.89803921568627454,0.85098039215686272,0.2196078431372549,1;rgb;ccw:0.609375;231,215,57,255,rgb:0.90588235294117647,0.84313725490196079,0.22352941176470589,1;rgb;ccw:0.613281;233,213,57,255,rgb:0.9137254901960784,0.83529411764705885,0.22352941176470589,1;rgb;ccw:0.617188;235,211,57,255,rgb:0.92156862745098034,0.82745098039215681,0.22352941176470589,1;rgb;ccw:0.621094;236,209,58,255,rgb:0.92549019607843142,0.81960784313725488,0.22745098039215686,1;rgb;ccw:0.625;238,207,58,255,rgb:0.93333333333333335,0.81176470588235294,0.22745098039215686,1;rgb;ccw:0.628906;239,205,58,255,rgb:0.93725490196078431,0.80392156862745101,0.22745098039215686,1;rgb;ccw:0.632813;241,203,58,255,rgb:0.94509803921568625,0.79607843137254897,0.22745098039215686,1;rgb;ccw:0.636719;242,201,58,255,rgb:0.94901960784313721,0.78823529411764703,0.22745098039215686,1;rgb;ccw:0.640625;244,199,58,255,rgb:0.95686274509803926,0.7803921568627451,0.22745098039215686,1;rgb;ccw:0.644531;245,197,58,255,rgb:0.96078431372549022,0.77254901960784317,0.22745098039215686,1;rgb;ccw:0.648438;246,195,58,255,rgb:0.96470588235294119,0.76470588235294112,0.22745098039215686,1;rgb;ccw:0.652344;247,193,58,255,rgb:0.96862745098039216,0.75686274509803919,0.22745098039215686,1;rgb;ccw:0.65625;248,190,57,255,rgb:0.97254901960784312,0.74509803921568629,0.22352941176470589,1;rgb;ccw:0.660156;249,188,57,255,rgb:0.97647058823529409,0.73725490196078436,0.22352941176470589,1;rgb;ccw:0.664063;250,186,57,255,rgb:0.98039215686274506,0.72941176470588232,0.22352941176470589,1;rgb;ccw:0.667969;251,184,56,255,rgb:0.98431372549019602,0.72156862745098038,0.2196078431372549,1;rgb;ccw:0.671875;251,182,55,255,rgb:0.98431372549019602,0.71372549019607845,0.21568627450980393,1;rgb;ccw:0.675781;252,179,54,255,rgb:0.9882352941176471,0.70196078431372544,0.21176470588235294,1;rgb;ccw:0.679688;252,177,54,255,rgb:0.9882352941176471,0.69411764705882351,0.21176470588235294,1;rgb;ccw:0.683594;253,174,53,255,rgb:0.99215686274509807,0.68235294117647061,0.20784313725490197,1;rgb;ccw:0.6875;253,172,52,255,rgb:0.99215686274509807,0.67450980392156867,0.20392156862745098,1;rgb;ccw:0.691406;254,169,51,255,rgb:0.99607843137254903,0.66274509803921566,0.20000000000000001,1;rgb;ccw:0.695313;254,167,50,255,rgb:0.99607843137254903,0.65490196078431373,0.19607843137254902,1;rgb;ccw:0.699219;254,164,49,255,rgb:0.99607843137254903,0.64313725490196083,0.19215686274509805,1;rgb;ccw:0.703125;254,161,48,255,rgb:0.99607843137254903,0.63137254901960782,0.18823529411764706,1;rgb;ccw:0.707031;254,158,47,255,rgb:0.99607843137254903,0.61960784313725492,0.18431372549019609,1;rgb;ccw:0.710938;254,155,45,255,rgb:0.99607843137254903,0.60784313725490191,0.17647058823529413,1;rgb;ccw:0.714844;254,153,44,255,rgb:0.99607843137254903,0.59999999999999998,0.17254901960784313,1;rgb;ccw:0.71875;254,150,43,255,rgb:0.99607843137254903,0.58823529411764708,0.16862745098039217,1;rgb;ccw:0.722656;254,147,42,255,rgb:0.99607843137254903,0.57647058823529407,0.16470588235294117,1;rgb;ccw:0.726563;254,144,41,255,rgb:0.99607843137254903,0.56470588235294117,0.16078431372549021,1;rgb;ccw:0.730469;253,141,39,255,rgb:0.99215686274509807,0.55294117647058827,0.15294117647058825,1;rgb;ccw:0.734375;253,138,38,255,rgb:0.99215686274509807,0.54117647058823526,0.14901960784313725,1;rgb;ccw:0.738281;252,135,37,255,rgb:0.9882352941176471,0.52941176470588236,0.14509803921568629,1;rgb;ccw:0.742188;252,132,35,255,rgb:0.9882352941176471,0.51764705882352946,0.13725490196078433,1;rgb;ccw:0.746094;251,129,34,255,rgb:0.98431372549019602,0.50588235294117645,0.13333333333333333,1;rgb;ccw:0.75;251,126,33,255,rgb:0.98431372549019602,0.49411764705882355,0.12941176470588237,1;rgb;ccw:0.753906;250,123,31,255,rgb:0.98039215686274506,0.4823529411764706,0.12156862745098039,1;rgb;ccw:0.757813;249,120,30,255,rgb:0.97647058823529409,0.47058823529411764,0.11764705882352941,1;rgb;ccw:0.761719;249,117,29,255,rgb:0.97647058823529409,0.45882352941176469,0.11372549019607843,1;rgb;ccw:0.765625;248,114,28,255,rgb:0.97254901960784312,0.44705882352941179,0.10980392156862745,1;rgb;ccw:0.769531;247,111,26,255,rgb:0.96862745098039216,0.43529411764705883,0.10196078431372549,1;rgb;ccw:0.773438;246,108,25,255,rgb:0.96470588235294119,0.42352941176470588,0.09803921568627451,1;rgb;ccw:0.777344;245,105,24,255,rgb:0.96078431372549022,0.41176470588235292,0.09411764705882353,1;rgb;ccw:0.78125;244,102,23,255,rgb:0.95686274509803926,0.40000000000000002,0.09019607843137255,1;rgb;ccw:0.785156;243,99,21,255,rgb:0.95294117647058818,0.38823529411764707,0.08235294117647059,1;rgb;ccw:0.789063;242,96,20,255,rgb:0.94901960784313721,0.37647058823529411,0.07843137254901961,1;rgb;ccw:0.792969;241,93,19,255,rgb:0.94509803921568625,0.36470588235294116,0.07450980392156863,1;rgb;ccw:0.796875;240,91,18,255,rgb:0.94117647058823528,0.35686274509803922,0.07058823529411765,1;rgb;ccw:0.800781;239,88,17,255,rgb:0.93725490196078431,0.34509803921568627,0.06666666666666667,1;rgb;ccw:0.804688;237,85,16,255,rgb:0.92941176470588238,0.33333333333333331,0.06274509803921569,1;rgb;ccw:0.808594;236,83,15,255,rgb:0.92549019607843142,0.32549019607843138,0.05882352941176471,1;rgb;ccw:0.8125;235,80,14,255,rgb:0.92156862745098034,0.31372549019607843,0.05490196078431372,1;rgb;ccw:0.816406;234,78,13,255,rgb:0.91764705882352937,0.30588235294117649,0.05098039215686274,1;rgb;ccw:0.820313;232,75,12,255,rgb:0.90980392156862744,0.29411764705882354,0.04705882352941176,1;rgb;ccw:0.824219;231,73,12,255,rgb:0.90588235294117647,0.28627450980392155,0.04705882352941176,1;rgb;ccw:0.828125;229,71,11,255,rgb:0.89803921568627454,0.27843137254901962,0.04313725490196078,1;rgb;ccw:0.832031;228,69,10,255,rgb:0.89411764705882357,0.27058823529411763,0.0392156862745098,1;rgb;ccw:0.835938;226,67,10,255,rgb:0.88627450980392153,0.2627450980392157,0.0392156862745098,1;rgb;ccw:0.839844;225,65,9,255,rgb:0.88235294117647056,0.25490196078431371,0.03529411764705882,1;rgb;ccw:0.84375;223,63,8,255,rgb:0.87450980392156863,0.24705882352941178,0.03137254901960784,1;rgb;ccw:0.847656;221,61,8,255,rgb:0.8666666666666667,0.23921568627450981,0.03137254901960784,1;rgb;ccw:0.851563;220,59,7,255,rgb:0.86274509803921573,0.23137254901960785,0.02745098039215686,1;rgb;ccw:0.855469;218,57,7,255,rgb:0.85490196078431369,0.22352941176470589,0.02745098039215686,1;rgb;ccw:0.859375;216,55,6,255,rgb:0.84705882352941175,0.21568627450980393,0.02352941176470588,1;rgb;ccw:0.863281;214,53,6,255,rgb:0.83921568627450982,0.20784313725490197,0.02352941176470588,1;rgb;ccw:0.867188;212,51,5,255,rgb:0.83137254901960789,0.20000000000000001,0.0196078431372549,1;rgb;ccw:0.871094;210,49,5,255,rgb:0.82352941176470584,0.19215686274509805,0.0196078431372549,1;rgb;ccw:0.875;208,47,5,255,rgb:0.81568627450980391,0.18431372549019609,0.0196078431372549,1;rgb;ccw:0.878906;206,45,4,255,rgb:0.80784313725490198,0.17647058823529413,0.01568627450980392,1;rgb;ccw:0.882813;204,43,4,255,rgb:0.80000000000000004,0.16862745098039217,0.01568627450980392,1;rgb;ccw:0.886719;202,42,4,255,rgb:0.792156862745098,0.16470588235294117,0.01568627450980392,1;rgb;ccw:0.890625;200,40,3,255,rgb:0.78431372549019607,0.15686274509803921,0.01176470588235294,1;rgb;ccw:0.894531;197,38,3,255,rgb:0.77254901960784317,0.14901960784313725,0.01176470588235294,1;rgb;ccw:0.898438;195,37,3,255,rgb:0.76470588235294112,0.14509803921568629,0.01176470588235294,1;rgb;ccw:0.902344;193,35,2,255,rgb:0.75686274509803919,0.13725490196078433,0.00784313725490196,1;rgb;ccw:0.90625;190,33,2,255,rgb:0.74509803921568629,0.12941176470588237,0.00784313725490196,1;rgb;ccw:0.910156;188,32,2,255,rgb:0.73725490196078436,0.12549019607843137,0.00784313725490196,1;rgb;ccw:0.914063;185,30,2,255,rgb:0.72549019607843135,0.11764705882352941,0.00784313725490196,1;rgb;ccw:0.917969;183,29,2,255,rgb:0.71764705882352942,0.11372549019607843,0.00784313725490196,1;rgb;ccw:0.921875;180,27,1,255,rgb:0.70588235294117652,0.10588235294117647,0.00392156862745098,1;rgb;ccw:0.925781;178,26,1,255,rgb:0.69803921568627447,0.10196078431372549,0.00392156862745098,1;rgb;ccw:0.929688;175,24,1,255,rgb:0.68627450980392157,0.09411764705882353,0.00392156862745098,1;rgb;ccw:0.933594;172,23,1,255,rgb:0.67450980392156867,0.09019607843137255,0.00392156862745098,1;rgb;ccw:0.9375;169,22,1,255,rgb:0.66274509803921566,0.08627450980392157,0.00392156862745098,1;rgb;ccw:0.941406;167,20,1,255,rgb:0.65490196078431373,0.07843137254901961,0.00392156862745098,1;rgb;ccw:0.945313;164,19,1,255,rgb:0.64313725490196083,0.07450980392156863,0.00392156862745098,1;rgb;ccw:0.949219;161,18,1,255,rgb:0.63137254901960782,0.07058823529411765,0.00392156862745098,1;rgb;ccw:0.953125;158,16,1,255,rgb:0.61960784313725492,0.06274509803921569,0.00392156862745098,1;rgb;ccw:0.957031;155,15,1,255,rgb:0.60784313725490191,0.05882352941176471,0.00392156862745098,1;rgb;ccw:0.960938;152,14,1,255,rgb:0.59607843137254901,0.05490196078431372,0.00392156862745098,1;rgb;ccw:0.964844;149,13,1,255,rgb:0.58431372549019611,0.05098039215686274,0.00392156862745098,1;rgb;ccw:0.96875;146,11,1,255,rgb:0.5725490196078431,0.04313725490196078,0.00392156862745098,1;rgb;ccw:0.972656;142,10,1,255,rgb:0.55686274509803924,0.0392156862745098,0.00392156862745098,1;rgb;ccw:0.976563;139,9,2,255,rgb:0.54509803921568623,0.03529411764705882,0.00784313725490196,1;rgb;ccw:0.980469;136,8,2,255,rgb:0.53333333333333333,0.03137254901960784,0.00784313725490196,1;rgb;ccw:0.984375;133,7,2,255,rgb:0.52156862745098043,0.02745098039215686,0.00784313725490196,1;rgb;ccw:0.988281;129,6,2,255,rgb:0.50588235294117645,0.02352941176470588,0.00784313725490196,1;rgb;ccw" name="stops"/>
                  </Option>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option type="QString" value="0" name="blend_mode"/>
                    <Option type="QString" value="2" name="draw_mode"/>
                    <Option type="QString" value="1" name="enabled"/>
                    <Option type="QString" value="1" name="opacity"/>
                  </Option>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option type="QString" value="13" name="blend_mode"/>
                    <Option type="QString" value="2.645" name="blur_level"/>
                    <Option type="QString" value="MM" name="blur_unit"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="blur_unit_scale"/>
                    <Option type="QString" value="0,0,0,255,rgb:0,0,0,1" name="color"/>
                    <Option type="QString" value="2" name="draw_mode"/>
                    <Option type="QString" value="0" name="enabled"/>
                    <Option type="QString" value="135" name="offset_angle"/>
                    <Option type="QString" value="2" name="offset_distance"/>
                    <Option type="QString" value="MM" name="offset_unit"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_unit_scale"/>
                    <Option type="QString" value="1" name="opacity"/>
                  </Option>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option type="QString" value="0" name="blend_mode"/>
                    <Option type="QString" value="2.645" name="blur_level"/>
                    <Option type="QString" value="MM" name="blur_unit"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="blur_unit_scale"/>
                    <Option type="QString" value="69,116,40,255,rgb:0.27058823529411763,0.45490196078431372,0.15686274509803921,1" name="color1"/>
                    <Option type="QString" value="188,220,60,255,rgb:0.73725490196078436,0.86274509803921573,0.23529411764705882,1" name="color2"/>
                    <Option type="QString" value="0" name="color_type"/>
                    <Option type="QString" value="ccw" name="direction"/>
                    <Option type="QString" value="0" name="discrete"/>
                    <Option type="QString" value="2" name="draw_mode"/>
                    <Option type="QString" value="0" name="enabled"/>
                    <Option type="QString" value="0.5" name="opacity"/>
                    <Option type="QString" value="gradient" name="rampType"/>
                    <Option type="QString" value="255,255,255,255,rgb:1,1,1,1" name="single_color"/>
                    <Option type="QString" value="rgb" name="spec"/>
                    <Option type="QString" value="2" name="spread"/>
                    <Option type="QString" value="MM" name="spread_unit"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="spread_unit_scale"/>
                  </Option>
                </effect>
              </effect>
            </text-buffer>
            <text-mask maskType="0" maskSize="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskedSymbolLayers="" maskEnabled="0" maskSize2="1.5" maskOpacity="1" maskJoinStyle="128" maskSizeUnits="MM"/>
            <background shapeSizeUnit="Point" shapeRadiiUnit="Point" shapeBorderColor="128,128,128,255,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,1" shapeRotationType="0" shapeBorderWidth="0" shapeRadiiY="0" shapeFillColor="255,255,255,255,rgb:1,1,1,1" shapeRadiiX="0" shapeOpacity="1" shapeSizeX="0" shapeDraw="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthUnit="Point" shapeJoinStyle="64" shapeRotation="0" shapeSizeY="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeType="0" shapeOffsetX="0" shapeBlendMode="0" shapeSVGFile="" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetY="0" shapeOffsetUnit="Point" shapeType="0">
              <symbol type="marker" name="markerSymbol" force_rhr="0" alpha="1" clip_to_extent="1" is_animated="0" frame_rate="10">
                <data_defined_properties>
                  <Option type="Map">
                    <Option type="QString" value="" name="name"/>
                    <Option name="properties"/>
                    <Option type="QString" value="collection" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer enabled="1" locked="0" class="SimpleMarker" pass="0" id="">
                  <Option type="Map">
                    <Option type="QString" value="0" name="angle"/>
                    <Option type="QString" value="square" name="cap_style"/>
                    <Option type="QString" value="152,125,183,255,rgb:0.59607843137254901,0.49019607843137253,0.71764705882352942,1" name="color"/>
                    <Option type="QString" value="1" name="horizontal_anchor_point"/>
                    <Option type="QString" value="bevel" name="joinstyle"/>
                    <Option type="QString" value="circle" name="name"/>
                    <Option type="QString" value="0,0" name="offset"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                    <Option type="QString" value="MM" name="offset_unit"/>
                    <Option type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" name="outline_color"/>
                    <Option type="QString" value="solid" name="outline_style"/>
                    <Option type="QString" value="0" name="outline_width"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale"/>
                    <Option type="QString" value="MM" name="outline_width_unit"/>
                    <Option type="QString" value="diameter" name="scale_method"/>
                    <Option type="QString" value="2" name="size"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="size_map_unit_scale"/>
                    <Option type="QString" value="MM" name="size_unit"/>
                    <Option type="QString" value="1" name="vertical_anchor_point"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option type="QString" value="" name="name"/>
                      <Option name="properties"/>
                      <Option type="QString" value="collection" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol type="fill" name="fillSymbol" force_rhr="0" alpha="1" clip_to_extent="1" is_animated="0" frame_rate="10">
                <data_defined_properties>
                  <Option type="Map">
                    <Option type="QString" value="" name="name"/>
                    <Option name="properties"/>
                    <Option type="QString" value="collection" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer enabled="1" locked="0" class="SimpleFill" pass="0" id="">
                  <Option type="Map">
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
                    <Option type="QString" value="255,255,255,255,rgb:1,1,1,1" name="color"/>
                    <Option type="QString" value="bevel" name="joinstyle"/>
                    <Option type="QString" value="0,0" name="offset"/>
                    <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                    <Option type="QString" value="MM" name="offset_unit"/>
                    <Option type="QString" value="128,128,128,255,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,1" name="outline_color"/>
                    <Option type="QString" value="no" name="outline_style"/>
                    <Option type="QString" value="0" name="outline_width"/>
                    <Option type="QString" value="Point" name="outline_width_unit"/>
                    <Option type="QString" value="solid" name="style"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option type="QString" value="" name="name"/>
                      <Option name="properties"/>
                      <Option type="QString" value="collection" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetDist="1" shadowOpacity="0.69999999999999996" shadowRadius="1.5" shadowRadiusUnit="MM" shadowDraw="0" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowScale="100" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetAngle="135" shadowUnder="0" shadowBlendMode="6" shadowOffsetUnit="MM" shadowOffsetGlobal="1" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format decimals="3" addDirectionSymbol="0" leftDirectionSymbol="&lt;" wrapChar="" useMaxLineLengthForAutoWrap="1" multilineAlign="3" reverseDirectionSymbol="0" placeDirectionSymbol="0" rightDirectionSymbol=">" autoWrapLength="0" formatNumbers="0" plussign="0"/>
          <placement placementFlags="10" distUnits="MM" rotationUnit="AngleDegrees" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" maximumDistanceUnit="MM" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" lineAnchorTextPoint="CenterOfText" quadOffset="4" maximumDistance="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistanceUnit="MM" xOffset="0" geometryGeneratorEnabled="0" lineAnchorPercent="0.5" centroidWhole="0" placement="0" priority="5" polygonPlacementFlags="2" centroidInside="0" yOffset="0" lineAnchorType="0" rotationAngle="0" offsetType="0" allowDegraded="0" overlapHandling="PreventOverlap" layerType="PolygonGeometry" repeatDistance="0" prioritization="PreferCloser" repeatDistanceUnits="MM" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" overrunDistance="0" maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" offsetUnits="MM" distMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleOut="-25" lineAnchorClipping="0" geometryGenerator="" maxCurvedCharAngleIn="25" geometryGeneratorType="PointGeometry" fitInPolygonOnly="0" dist="0" preserveRotation="1"/>
          <rendering maxNumLabels="2000" scaleMax="0" upsidedownLabels="0" scaleMin="0" fontMinPixelSize="3" scaleVisibility="0" unplacedVisibility="0" fontLimitPixelSize="0" obstacle="1" minFeatureSize="0" labelPerPart="0" obstacleType="1" mergeLines="0" limitNumLabels="0" fontMaxPixelSize="10000" zIndex="0" drawLabels="1" obstacleFactor="1"/>
          <dd_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option type="QString" value="pole_of_inaccessibility" name="anchorPoint"/>
              <Option type="int" value="0" name="blendMode"/>
              <Option type="Map" name="ddProperties">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
              <Option type="bool" value="false" name="drawToAllParts"/>
              <Option type="QString" value="0" name="enabled"/>
              <Option type="QString" value="point_on_exterior" name="labelAnchorPoint"/>
              <Option type="QString" value="&lt;symbol type=&quot;line&quot; name=&quot;symbol&quot; force_rhr=&quot;0&quot; alpha=&quot;1&quot; clip_to_extent=&quot;1&quot; is_animated=&quot;0&quot; frame_rate=&quot;10&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; value=&quot;&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;collection&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer enabled=&quot;1&quot; locked=&quot;0&quot; class=&quot;SimpleLine&quot; pass=&quot;0&quot; id=&quot;{57960e07-bb1d-44af-9984-dfbe77717d6e}&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;align_dash_pattern&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;square&quot; name=&quot;capstyle&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;5;2&quot; name=&quot;customdash&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;customdash_map_unit_scale&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;MM&quot; name=&quot;customdash_unit&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;dash_pattern_offset&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;MM&quot; name=&quot;dash_pattern_offset_unit&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;draw_inside_polygon&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;bevel&quot; name=&quot;joinstyle&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot; name=&quot;line_color&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;solid&quot; name=&quot;line_style&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0.3&quot; name=&quot;line_width&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;MM&quot; name=&quot;line_width_unit&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;offset&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;offset_map_unit_scale&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;MM&quot; name=&quot;offset_unit&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;ring_filter&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;trim_distance_end&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;trim_distance_end_map_unit_scale&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;MM&quot; name=&quot;trim_distance_end_unit&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;trim_distance_start&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;trim_distance_start_map_unit_scale&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;MM&quot; name=&quot;trim_distance_start_unit&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;use_custom_dash&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;width_map_unit_scale&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; value=&quot;&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;collection&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" name="lineSymbol"/>
              <Option type="double" value="0" name="minLength"/>
              <Option type="QString" value="3x:0,0,0,0,0,0" name="minLengthMapUnitScale"/>
              <Option type="QString" value="MM" name="minLengthUnit"/>
              <Option type="double" value="0" name="offsetFromAnchor"/>
              <Option type="QString" value="3x:0,0,0,0,0,0" name="offsetFromAnchorMapUnitScale"/>
              <Option type="QString" value="MM" name="offsetFromAnchorUnit"/>
              <Option type="double" value="0" name="offsetFromLabel"/>
              <Option type="QString" value="3x:0,0,0,0,0,0" name="offsetFromLabelMapUnitScale"/>
              <Option type="QString" value="MM" name="offsetFromLabelUnit"/>
            </Option>
          </callout>
        </settings>
      </rule>
    </rules>
  </labeling>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerGeometryType>2</layerGeometryType>
</qgis>
