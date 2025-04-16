<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyDrawingTol="1" symbologyReferenceScale="-1" simplifyLocal="1" minScale="100000000" simplifyDrawingHints="1" simplifyMaxScale="1" hasScaleBasedVisibilityFlag="0" simplifyAlgorithm="0" readOnly="0" labelsEnabled="1" styleCategories="AllStyleCategories" version="3.22.1-Białowieża" maxScale="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal startField="" accumulate="0" startExpression="" durationField="" endField="" durationUnit="min" fixedDuration="0" endExpression="" mode="0" limitMode="0" enabled="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 enableorderby="0" forceraster="0" referencescale="-1" type="RuleRenderer" symbollevels="0">
    <rules key="{1c3604c6-4654-4249-ba2b-2873159958c2}">
      <rule symbol="0" label="Vértices" key="{324bda6b-3296-4d35-ab39-0ba34b525dd1}"/>
      <rule symbol="1" label="Distâncias" key="{9c60d1d1-614c-47df-8acb-3444f2137717}"/>
      <rule symbol="2" label="Azimutes" key="{626271a3-13c1-48dc-b69a-db246e1b6fa9}"/>
      <rule symbol="3" label="Área" key="{3cabcc2c-03c1-4bc2-8f3e-291d0a7ad946}"/>
    </rules>
    <symbols>
      <symbol name="0" alpha="1" force_rhr="0" clip_to_extent="1" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" value="" type="QString"/>
            <Option name="properties"/>
            <Option name="type" value="collection" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer class="GeometryGenerator" locked="0" enabled="1" pass="2">
          <Option type="Map">
            <Option name="SymbolType" value="Marker" type="QString"/>
            <Option name="geometryModifier" value="nodes_to_points( $geometry)" type="QString"/>
            <Option name="units" value="MapUnit" type="QString"/>
          </Option>
          <prop k="SymbolType" v="Marker"/>
          <prop k="geometryModifier" v="nodes_to_points( $geometry)"/>
          <prop k="units" v="MapUnit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" value="" type="QString"/>
              <Option name="properties"/>
              <Option name="type" value="collection" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol name="@0@0" alpha="1" force_rhr="0" clip_to_extent="1" type="marker">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" value="" type="QString"/>
                <Option name="properties"/>
                <Option name="type" value="collection" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="FontMarker" locked="0" enabled="1" pass="0">
              <Option type="Map">
                <Option name="angle" value="0" type="QString"/>
                <Option name="chr" value="A" type="QString"/>
                <Option name="color" value="31,31,31,255" type="QString"/>
                <Option name="font" value="Arial Black" type="QString"/>
                <Option name="font_style" value="Normal" type="QString"/>
                <Option name="horizontal_anchor_point" value="1" type="QString"/>
                <Option name="joinstyle" value="bevel" type="QString"/>
                <Option name="offset" value="0,-9" type="QString"/>
                <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_unit" value="Point" type="QString"/>
                <Option name="outline_color" value="35,35,35,255" type="QString"/>
                <Option name="outline_width" value="0" type="QString"/>
                <Option name="outline_width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="outline_width_unit" value="MM" type="QString"/>
                <Option name="size" value="10" type="QString"/>
                <Option name="size_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="size_unit" value="Point" type="QString"/>
                <Option name="vertical_anchor_point" value="1" type="QString"/>
              </Option>
              <prop k="angle" v="0"/>
              <prop k="chr" v="A"/>
              <prop k="color" v="31,31,31,255"/>
              <prop k="font" v="Arial Black"/>
              <prop k="font_style" v="Normal"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,-9"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="Point"/>
              <prop k="outline_color" v="35,35,35,255"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="size" v="10"/>
              <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="size_unit" v="Point"/>
              <prop k="vertical_anchor_point" v="1"/>
              <effect type="effectStack" enabled="1">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option name="blend_mode" value="13" type="QString"/>
                    <Option name="blur_level" value="2.645" type="QString"/>
                    <Option name="blur_unit" value="MM" type="QString"/>
                    <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="color" value="0,0,0,255" type="QString"/>
                    <Option name="draw_mode" value="2" type="QString"/>
                    <Option name="enabled" value="0" type="QString"/>
                    <Option name="offset_angle" value="135" type="QString"/>
                    <Option name="offset_distance" value="2" type="QString"/>
                    <Option name="offset_unit" value="MM" type="QString"/>
                    <Option name="offset_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="opacity" value="1" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option name="blend_mode" value="0" type="QString"/>
                    <Option name="blur_level" value="1" type="QString"/>
                    <Option name="blur_unit" value="MM" type="QString"/>
                    <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="color1" value="69,116,40,255" type="QString"/>
                    <Option name="color2" value="188,220,60,255" type="QString"/>
                    <Option name="color_type" value="0" type="QString"/>
                    <Option name="discrete" value="0" type="QString"/>
                    <Option name="draw_mode" value="2" type="QString"/>
                    <Option name="enabled" value="1" type="QString"/>
                    <Option name="opacity" value="0.5" type="QString"/>
                    <Option name="rampType" value="gradient" type="QString"/>
                    <Option name="single_color" value="255,255,0,255" type="QString"/>
                    <Option name="spread" value="2.5" type="QString"/>
                    <Option name="spread_unit" value="MM" type="QString"/>
                    <Option name="spread_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="1"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="69,116,40,255"/>
                  <prop k="color2" v="188,220,60,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,0,255"/>
                  <prop k="spread" v="2.5"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option name="blend_mode" value="0" type="QString"/>
                    <Option name="draw_mode" value="2" type="QString"/>
                    <Option name="enabled" value="1" type="QString"/>
                    <Option name="opacity" value="1" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option name="blend_mode" value="13" type="QString"/>
                    <Option name="blur_level" value="2.645" type="QString"/>
                    <Option name="blur_unit" value="MM" type="QString"/>
                    <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="color" value="0,0,0,255" type="QString"/>
                    <Option name="draw_mode" value="2" type="QString"/>
                    <Option name="enabled" value="0" type="QString"/>
                    <Option name="offset_angle" value="135" type="QString"/>
                    <Option name="offset_distance" value="2" type="QString"/>
                    <Option name="offset_unit" value="MM" type="QString"/>
                    <Option name="offset_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="opacity" value="1" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option name="blend_mode" value="0" type="QString"/>
                    <Option name="blur_level" value="2.645" type="QString"/>
                    <Option name="blur_unit" value="MM" type="QString"/>
                    <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="color1" value="69,116,40,255" type="QString"/>
                    <Option name="color2" value="188,220,60,255" type="QString"/>
                    <Option name="color_type" value="0" type="QString"/>
                    <Option name="discrete" value="0" type="QString"/>
                    <Option name="draw_mode" value="2" type="QString"/>
                    <Option name="enabled" value="0" type="QString"/>
                    <Option name="opacity" value="0.5" type="QString"/>
                    <Option name="rampType" value="gradient" type="QString"/>
                    <Option name="single_color" value="255,255,255,255" type="QString"/>
                    <Option name="spread" value="2" type="QString"/>
                    <Option name="spread_unit" value="MM" type="QString"/>
                    <Option name="spread_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="69,116,40,255"/>
                  <prop k="color2" v="188,220,60,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" value="" type="QString"/>
                  <Option name="properties" type="Map">
                    <Option name="char" type="Map">
                      <Option name="active" value="true" type="bool"/>
                      <Option name="expression" value="if (@geometry_part_num =  @geometry_part_count , '',&#xd;&#xa;'V-' ||  lpad( @geometry_part_num  ,2, '0')&#xd;&#xa;)" type="QString"/>
                      <Option name="type" value="3" type="int"/>
                    </Option>
                  </Option>
                  <Option name="type" value="collection" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
            <layer class="SimpleMarker" locked="0" enabled="1" pass="0">
              <Option type="Map">
                <Option name="angle" value="0" type="QString"/>
                <Option name="cap_style" value="square" type="QString"/>
                <Option name="color" value="31,31,31,255" type="QString"/>
                <Option name="horizontal_anchor_point" value="1" type="QString"/>
                <Option name="joinstyle" value="bevel" type="QString"/>
                <Option name="name" value="square" type="QString"/>
                <Option name="offset" value="0,0" type="QString"/>
                <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_unit" value="MM" type="QString"/>
                <Option name="outline_color" value="35,35,35,255" type="QString"/>
                <Option name="outline_style" value="solid" type="QString"/>
                <Option name="outline_width" value="0" type="QString"/>
                <Option name="outline_width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="outline_width_unit" value="MM" type="QString"/>
                <Option name="scale_method" value="diameter" type="QString"/>
                <Option name="size" value="1" type="QString"/>
                <Option name="size_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="size_unit" value="MM" type="QString"/>
                <Option name="vertical_anchor_point" value="1" type="QString"/>
              </Option>
              <prop k="angle" v="0"/>
              <prop k="cap_style" v="square"/>
              <prop k="color" v="31,31,31,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="square"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="scale_method" v="diameter"/>
              <prop k="size" v="1"/>
              <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="size_unit" v="MM"/>
              <prop k="vertical_anchor_point" v="1"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" value="" type="QString"/>
                  <Option name="properties"/>
                  <Option name="type" value="collection" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="1" alpha="1" force_rhr="0" clip_to_extent="1" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" value="" type="QString"/>
            <Option name="properties"/>
            <Option name="type" value="collection" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer class="GeometryGenerator" locked="0" enabled="1" pass="1">
          <Option type="Map">
            <Option name="SymbolType" value="Line" type="QString"/>
            <Option name="geometryModifier" value=" segments_to_lines( $geometry )" type="QString"/>
            <Option name="units" value="MapUnit" type="QString"/>
          </Option>
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v=" segments_to_lines( $geometry )"/>
          <prop k="units" v="MapUnit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" value="" type="QString"/>
              <Option name="properties"/>
              <Option name="type" value="collection" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol name="@1@0" alpha="1" force_rhr="0" clip_to_extent="1" type="line">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" value="" type="QString"/>
                <Option name="properties"/>
                <Option name="type" value="collection" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="ArrowLine" locked="0" enabled="1" pass="0">
              <Option type="Map">
                <Option name="arrow_start_width" value="1" type="QString"/>
                <Option name="arrow_start_width_unit" value="MM" type="QString"/>
                <Option name="arrow_start_width_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="arrow_type" value="0" type="QString"/>
                <Option name="arrow_width" value="0" type="QString"/>
                <Option name="arrow_width_unit" value="MM" type="QString"/>
                <Option name="arrow_width_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="head_length" value="1.5" type="QString"/>
                <Option name="head_length_unit" value="MM" type="QString"/>
                <Option name="head_length_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="head_thickness" value="1.5" type="QString"/>
                <Option name="head_thickness_unit" value="MM" type="QString"/>
                <Option name="head_thickness_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="head_type" value="2" type="QString"/>
                <Option name="is_curved" value="1" type="QString"/>
                <Option name="is_repeated" value="1" type="QString"/>
                <Option name="offset" value="-5" type="QString"/>
                <Option name="offset_unit" value="MM" type="QString"/>
                <Option name="offset_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="ring_filter" value="0" type="QString"/>
              </Option>
              <prop k="arrow_start_width" v="1"/>
              <prop k="arrow_start_width_unit" v="MM"/>
              <prop k="arrow_start_width_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="arrow_type" v="0"/>
              <prop k="arrow_width" v="0"/>
              <prop k="arrow_width_unit" v="MM"/>
              <prop k="arrow_width_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="head_length" v="1.5"/>
              <prop k="head_length_unit" v="MM"/>
              <prop k="head_length_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="head_thickness" v="1.5"/>
              <prop k="head_thickness_unit" v="MM"/>
              <prop k="head_thickness_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="head_type" v="2"/>
              <prop k="is_curved" v="1"/>
              <prop k="is_repeated" v="1"/>
              <prop k="offset" v="-5"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="ring_filter" v="0"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" value="" type="QString"/>
                  <Option name="properties"/>
                  <Option name="type" value="collection" type="QString"/>
                </Option>
              </data_defined_properties>
              <symbol name="@@1@0@0" alpha="1" force_rhr="0" clip_to_extent="1" type="fill">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" value="" type="QString"/>
                    <Option name="properties"/>
                    <Option name="type" value="collection" type="QString"/>
                  </Option>
                </data_defined_properties>
                <layer class="SimpleFill" locked="0" enabled="1" pass="0">
                  <Option type="Map">
                    <Option name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="color" value="31,31,31,255" type="QString"/>
                    <Option name="joinstyle" value="bevel" type="QString"/>
                    <Option name="offset" value="0,0" type="QString"/>
                    <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="offset_unit" value="MM" type="QString"/>
                    <Option name="outline_color" value="35,35,35,255" type="QString"/>
                    <Option name="outline_style" value="solid" type="QString"/>
                    <Option name="outline_width" value="0.26" type="QString"/>
                    <Option name="outline_width_unit" value="MM" type="QString"/>
                    <Option name="style" value="solid" type="QString"/>
                  </Option>
                  <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="31,31,31,255"/>
                  <prop k="joinstyle" v="bevel"/>
                  <prop k="offset" v="0,0"/>
                  <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="outline_color" v="35,35,35,255"/>
                  <prop k="outline_style" v="solid"/>
                  <prop k="outline_width" v="0.26"/>
                  <prop k="outline_width_unit" v="MM"/>
                  <prop k="style" v="solid"/>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" value="" type="QString"/>
                      <Option name="properties"/>
                      <Option name="type" value="collection" type="QString"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
            <layer class="MarkerLine" locked="0" enabled="1" pass="0">
              <Option type="Map">
                <Option name="average_angle_length" value="4" type="QString"/>
                <Option name="average_angle_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="average_angle_unit" value="MM" type="QString"/>
                <Option name="interval" value="3" type="QString"/>
                <Option name="interval_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="interval_unit" value="MM" type="QString"/>
                <Option name="offset" value="-5" type="QString"/>
                <Option name="offset_along_line" value="0" type="QString"/>
                <Option name="offset_along_line_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_along_line_unit" value="MM" type="QString"/>
                <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_unit" value="MM" type="QString"/>
                <Option name="placement" value="centralpoint" type="QString"/>
                <Option name="ring_filter" value="0" type="QString"/>
                <Option name="rotate" value="1" type="QString"/>
              </Option>
              <prop k="average_angle_length" v="4"/>
              <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="average_angle_unit" v="MM"/>
              <prop k="interval" v="3"/>
              <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="interval_unit" v="MM"/>
              <prop k="offset" v="-5"/>
              <prop k="offset_along_line" v="0"/>
              <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_along_line_unit" v="MM"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="placement" v="centralpoint"/>
              <prop k="ring_filter" v="0"/>
              <prop k="rotate" v="1"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" value="" type="QString"/>
                  <Option name="properties"/>
                  <Option name="type" value="collection" type="QString"/>
                </Option>
              </data_defined_properties>
              <symbol name="@@1@0@1" alpha="1" force_rhr="0" clip_to_extent="1" type="marker">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" value="" type="QString"/>
                    <Option name="properties"/>
                    <Option name="type" value="collection" type="QString"/>
                  </Option>
                </data_defined_properties>
                <layer class="FontMarker" locked="0" enabled="1" pass="0">
                  <Option type="Map">
                    <Option name="angle" value="0" type="QString"/>
                    <Option name="chr" value="A" type="QString"/>
                    <Option name="color" value="31,31,31,255" type="QString"/>
                    <Option name="font" value="Arial Black" type="QString"/>
                    <Option name="font_style" value="Normal" type="QString"/>
                    <Option name="horizontal_anchor_point" value="1" type="QString"/>
                    <Option name="joinstyle" value="bevel" type="QString"/>
                    <Option name="offset" value="0,-7" type="QString"/>
                    <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="offset_unit" value="Point" type="QString"/>
                    <Option name="outline_color" value="35,35,35,255" type="QString"/>
                    <Option name="outline_width" value="0" type="QString"/>
                    <Option name="outline_width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="outline_width_unit" value="MM" type="QString"/>
                    <Option name="size" value="10" type="QString"/>
                    <Option name="size_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="size_unit" value="Point" type="QString"/>
                    <Option name="vertical_anchor_point" value="1" type="QString"/>
                  </Option>
                  <prop k="angle" v="0"/>
                  <prop k="chr" v="A"/>
                  <prop k="color" v="31,31,31,255"/>
                  <prop k="font" v="Arial Black"/>
                  <prop k="font_style" v="Normal"/>
                  <prop k="horizontal_anchor_point" v="1"/>
                  <prop k="joinstyle" v="bevel"/>
                  <prop k="offset" v="0,-7"/>
                  <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="offset_unit" v="Point"/>
                  <prop k="outline_color" v="35,35,35,255"/>
                  <prop k="outline_width" v="0"/>
                  <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="outline_width_unit" v="MM"/>
                  <prop k="size" v="10"/>
                  <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="size_unit" v="Point"/>
                  <prop k="vertical_anchor_point" v="1"/>
                  <effect type="effectStack" enabled="1">
                    <effect type="dropShadow">
                      <Option type="Map">
                        <Option name="blend_mode" value="13" type="QString"/>
                        <Option name="blur_level" value="2.645" type="QString"/>
                        <Option name="blur_unit" value="MM" type="QString"/>
                        <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                        <Option name="color" value="0,0,0,255" type="QString"/>
                        <Option name="draw_mode" value="2" type="QString"/>
                        <Option name="enabled" value="0" type="QString"/>
                        <Option name="offset_angle" value="135" type="QString"/>
                        <Option name="offset_distance" value="2" type="QString"/>
                        <Option name="offset_unit" value="MM" type="QString"/>
                        <Option name="offset_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                        <Option name="opacity" value="1" type="QString"/>
                      </Option>
                      <prop k="blend_mode" v="13"/>
                      <prop k="blur_level" v="2.645"/>
                      <prop k="blur_unit" v="MM"/>
                      <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                      <prop k="color" v="0,0,0,255"/>
                      <prop k="draw_mode" v="2"/>
                      <prop k="enabled" v="0"/>
                      <prop k="offset_angle" v="135"/>
                      <prop k="offset_distance" v="2"/>
                      <prop k="offset_unit" v="MM"/>
                      <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                      <prop k="opacity" v="1"/>
                    </effect>
                    <effect type="outerGlow">
                      <Option type="Map">
                        <Option name="blend_mode" value="0" type="QString"/>
                        <Option name="blur_level" value="1" type="QString"/>
                        <Option name="blur_unit" value="MM" type="QString"/>
                        <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                        <Option name="color1" value="69,116,40,255" type="QString"/>
                        <Option name="color2" value="188,220,60,255" type="QString"/>
                        <Option name="color_type" value="0" type="QString"/>
                        <Option name="discrete" value="0" type="QString"/>
                        <Option name="draw_mode" value="2" type="QString"/>
                        <Option name="enabled" value="1" type="QString"/>
                        <Option name="opacity" value="0.5" type="QString"/>
                        <Option name="rampType" value="gradient" type="QString"/>
                        <Option name="single_color" value="255,255,255,255" type="QString"/>
                        <Option name="spread" value="2.5" type="QString"/>
                        <Option name="spread_unit" value="MM" type="QString"/>
                        <Option name="spread_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                      </Option>
                      <prop k="blend_mode" v="0"/>
                      <prop k="blur_level" v="1"/>
                      <prop k="blur_unit" v="MM"/>
                      <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                      <prop k="color1" v="69,116,40,255"/>
                      <prop k="color2" v="188,220,60,255"/>
                      <prop k="color_type" v="0"/>
                      <prop k="discrete" v="0"/>
                      <prop k="draw_mode" v="2"/>
                      <prop k="enabled" v="1"/>
                      <prop k="opacity" v="0.5"/>
                      <prop k="rampType" v="gradient"/>
                      <prop k="single_color" v="255,255,255,255"/>
                      <prop k="spread" v="2.5"/>
                      <prop k="spread_unit" v="MM"/>
                      <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                    </effect>
                    <effect type="drawSource">
                      <Option type="Map">
                        <Option name="blend_mode" value="0" type="QString"/>
                        <Option name="draw_mode" value="2" type="QString"/>
                        <Option name="enabled" value="1" type="QString"/>
                        <Option name="opacity" value="1" type="QString"/>
                      </Option>
                      <prop k="blend_mode" v="0"/>
                      <prop k="draw_mode" v="2"/>
                      <prop k="enabled" v="1"/>
                      <prop k="opacity" v="1"/>
                    </effect>
                    <effect type="innerShadow">
                      <Option type="Map">
                        <Option name="blend_mode" value="13" type="QString"/>
                        <Option name="blur_level" value="2.645" type="QString"/>
                        <Option name="blur_unit" value="MM" type="QString"/>
                        <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                        <Option name="color" value="0,0,0,255" type="QString"/>
                        <Option name="draw_mode" value="2" type="QString"/>
                        <Option name="enabled" value="0" type="QString"/>
                        <Option name="offset_angle" value="135" type="QString"/>
                        <Option name="offset_distance" value="2" type="QString"/>
                        <Option name="offset_unit" value="MM" type="QString"/>
                        <Option name="offset_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                        <Option name="opacity" value="1" type="QString"/>
                      </Option>
                      <prop k="blend_mode" v="13"/>
                      <prop k="blur_level" v="2.645"/>
                      <prop k="blur_unit" v="MM"/>
                      <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                      <prop k="color" v="0,0,0,255"/>
                      <prop k="draw_mode" v="2"/>
                      <prop k="enabled" v="0"/>
                      <prop k="offset_angle" v="135"/>
                      <prop k="offset_distance" v="2"/>
                      <prop k="offset_unit" v="MM"/>
                      <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                      <prop k="opacity" v="1"/>
                    </effect>
                    <effect type="innerGlow">
                      <Option type="Map">
                        <Option name="blend_mode" value="0" type="QString"/>
                        <Option name="blur_level" value="2.645" type="QString"/>
                        <Option name="blur_unit" value="MM" type="QString"/>
                        <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                        <Option name="color1" value="69,116,40,255" type="QString"/>
                        <Option name="color2" value="188,220,60,255" type="QString"/>
                        <Option name="color_type" value="0" type="QString"/>
                        <Option name="discrete" value="0" type="QString"/>
                        <Option name="draw_mode" value="2" type="QString"/>
                        <Option name="enabled" value="0" type="QString"/>
                        <Option name="opacity" value="0.5" type="QString"/>
                        <Option name="rampType" value="gradient" type="QString"/>
                        <Option name="single_color" value="255,255,255,255" type="QString"/>
                        <Option name="spread" value="2" type="QString"/>
                        <Option name="spread_unit" value="MM" type="QString"/>
                        <Option name="spread_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                      </Option>
                      <prop k="blend_mode" v="0"/>
                      <prop k="blur_level" v="2.645"/>
                      <prop k="blur_unit" v="MM"/>
                      <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                      <prop k="color1" v="69,116,40,255"/>
                      <prop k="color2" v="188,220,60,255"/>
                      <prop k="color_type" v="0"/>
                      <prop k="discrete" v="0"/>
                      <prop k="draw_mode" v="2"/>
                      <prop k="enabled" v="0"/>
                      <prop k="opacity" v="0.5"/>
                      <prop k="rampType" v="gradient"/>
                      <prop k="single_color" v="255,255,255,255"/>
                      <prop k="spread" v="2"/>
                      <prop k="spread_unit" v="MM"/>
                      <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                    </effect>
                  </effect>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" value="" type="QString"/>
                      <Option name="properties" type="Map">
                        <Option name="char" type="Map">
                          <Option name="active" value="true" type="bool"/>
                          <Option name="expression" value="to_string(&#xd;&#xa;format_number(&#xd;&#xa;distance(&#xd;&#xa;start_point(geometry_n(  $geometry,  @geometry_part_num )), end_point(geometry_n(  $geometry,  @geometry_part_num ))&#xd;&#xa;)&#xd;&#xa;,2)&#xd;&#xa;)  ||  ' m'" type="QString"/>
                          <Option name="type" value="3" type="int"/>
                        </Option>
                      </Option>
                      <Option name="type" value="collection" type="QString"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
            <layer class="SimpleLine" locked="0" enabled="1" pass="0">
              <Option type="Map">
                <Option name="align_dash_pattern" value="0" type="QString"/>
                <Option name="capstyle" value="square" type="QString"/>
                <Option name="customdash" value="5;2" type="QString"/>
                <Option name="customdash_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="customdash_unit" value="MM" type="QString"/>
                <Option name="dash_pattern_offset" value="0" type="QString"/>
                <Option name="dash_pattern_offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="dash_pattern_offset_unit" value="MM" type="QString"/>
                <Option name="draw_inside_polygon" value="0" type="QString"/>
                <Option name="joinstyle" value="bevel" type="QString"/>
                <Option name="line_color" value="35,35,35,255" type="QString"/>
                <Option name="line_style" value="solid" type="QString"/>
                <Option name="line_width" value="0.4" type="QString"/>
                <Option name="line_width_unit" value="MM" type="QString"/>
                <Option name="offset" value="-5" type="QString"/>
                <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_unit" value="MM" type="QString"/>
                <Option name="ring_filter" value="0" type="QString"/>
                <Option name="trim_distance_end" value="0" type="QString"/>
                <Option name="trim_distance_end_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="trim_distance_end_unit" value="MM" type="QString"/>
                <Option name="trim_distance_start" value="0" type="QString"/>
                <Option name="trim_distance_start_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="trim_distance_start_unit" value="MM" type="QString"/>
                <Option name="tweak_dash_pattern_on_corners" value="0" type="QString"/>
                <Option name="use_custom_dash" value="0" type="QString"/>
                <Option name="width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="square"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="line_color" v="35,35,35,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="0.4"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="-5"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" value="" type="QString"/>
                  <Option name="properties"/>
                  <Option name="type" value="collection" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
            <layer class="MarkerLine" locked="0" enabled="1" pass="0">
              <Option type="Map">
                <Option name="average_angle_length" value="4" type="QString"/>
                <Option name="average_angle_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="average_angle_unit" value="MM" type="QString"/>
                <Option name="interval" value="3" type="QString"/>
                <Option name="interval_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="interval_unit" value="MM" type="QString"/>
                <Option name="offset" value="-5" type="QString"/>
                <Option name="offset_along_line" value="0" type="QString"/>
                <Option name="offset_along_line_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_along_line_unit" value="MM" type="QString"/>
                <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_unit" value="MM" type="QString"/>
                <Option name="placement" value="vertex" type="QString"/>
                <Option name="ring_filter" value="0" type="QString"/>
                <Option name="rotate" value="1" type="QString"/>
              </Option>
              <prop k="average_angle_length" v="4"/>
              <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="average_angle_unit" v="MM"/>
              <prop k="interval" v="3"/>
              <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="interval_unit" v="MM"/>
              <prop k="offset" v="-5"/>
              <prop k="offset_along_line" v="0"/>
              <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_along_line_unit" v="MM"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="placement" v="vertex"/>
              <prop k="ring_filter" v="0"/>
              <prop k="rotate" v="1"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" value="" type="QString"/>
                  <Option name="properties"/>
                  <Option name="type" value="collection" type="QString"/>
                </Option>
              </data_defined_properties>
              <symbol name="@@1@0@3" alpha="1" force_rhr="0" clip_to_extent="1" type="marker">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" value="" type="QString"/>
                    <Option name="properties"/>
                    <Option name="type" value="collection" type="QString"/>
                  </Option>
                </data_defined_properties>
                <layer class="SimpleMarker" locked="0" enabled="1" pass="0">
                  <Option type="Map">
                    <Option name="angle" value="0" type="QString"/>
                    <Option name="cap_style" value="square" type="QString"/>
                    <Option name="color" value="255,0,0,255" type="QString"/>
                    <Option name="horizontal_anchor_point" value="1" type="QString"/>
                    <Option name="joinstyle" value="bevel" type="QString"/>
                    <Option name="name" value="line" type="QString"/>
                    <Option name="offset" value="0,0" type="QString"/>
                    <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="offset_unit" value="MM" type="QString"/>
                    <Option name="outline_color" value="35,35,35,255" type="QString"/>
                    <Option name="outline_style" value="solid" type="QString"/>
                    <Option name="outline_width" value="0.3" type="QString"/>
                    <Option name="outline_width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="outline_width_unit" value="MM" type="QString"/>
                    <Option name="scale_method" value="diameter" type="QString"/>
                    <Option name="size" value="10" type="QString"/>
                    <Option name="size_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="size_unit" value="MM" type="QString"/>
                    <Option name="vertical_anchor_point" value="1" type="QString"/>
                  </Option>
                  <prop k="angle" v="0"/>
                  <prop k="cap_style" v="square"/>
                  <prop k="color" v="255,0,0,255"/>
                  <prop k="horizontal_anchor_point" v="1"/>
                  <prop k="joinstyle" v="bevel"/>
                  <prop k="name" v="line"/>
                  <prop k="offset" v="0,0"/>
                  <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="outline_color" v="35,35,35,255"/>
                  <prop k="outline_style" v="solid"/>
                  <prop k="outline_width" v="0.3"/>
                  <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="outline_width_unit" v="MM"/>
                  <prop k="scale_method" v="diameter"/>
                  <prop k="size" v="10"/>
                  <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="size_unit" v="MM"/>
                  <prop k="vertical_anchor_point" v="1"/>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" value="" type="QString"/>
                      <Option name="properties"/>
                      <Option name="type" value="collection" type="QString"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="2" alpha="1" force_rhr="0" clip_to_extent="1" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" value="" type="QString"/>
            <Option name="properties"/>
            <Option name="type" value="collection" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer class="GeometryGenerator" locked="0" enabled="1" pass="1">
          <Option type="Map">
            <Option name="SymbolType" value="Line" type="QString"/>
            <Option name="geometryModifier" value=" segments_to_lines( $geometry )" type="QString"/>
            <Option name="units" value="MapUnit" type="QString"/>
          </Option>
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v=" segments_to_lines( $geometry )"/>
          <prop k="units" v="MapUnit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" value="" type="QString"/>
              <Option name="properties"/>
              <Option name="type" value="collection" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol name="@2@0" alpha="1" force_rhr="0" clip_to_extent="1" type="line">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" value="" type="QString"/>
                <Option name="properties"/>
                <Option name="type" value="collection" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="ArrowLine" locked="0" enabled="1" pass="0">
              <Option type="Map">
                <Option name="arrow_start_width" value="1" type="QString"/>
                <Option name="arrow_start_width_unit" value="MM" type="QString"/>
                <Option name="arrow_start_width_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="arrow_type" value="0" type="QString"/>
                <Option name="arrow_width" value="0" type="QString"/>
                <Option name="arrow_width_unit" value="MM" type="QString"/>
                <Option name="arrow_width_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="head_length" value="1.5" type="QString"/>
                <Option name="head_length_unit" value="MM" type="QString"/>
                <Option name="head_length_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="head_thickness" value="1.5" type="QString"/>
                <Option name="head_thickness_unit" value="MM" type="QString"/>
                <Option name="head_thickness_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="head_type" value="2" type="QString"/>
                <Option name="is_curved" value="1" type="QString"/>
                <Option name="is_repeated" value="1" type="QString"/>
                <Option name="offset" value="-5" type="QString"/>
                <Option name="offset_unit" value="MM" type="QString"/>
                <Option name="offset_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="ring_filter" value="0" type="QString"/>
              </Option>
              <prop k="arrow_start_width" v="1"/>
              <prop k="arrow_start_width_unit" v="MM"/>
              <prop k="arrow_start_width_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="arrow_type" v="0"/>
              <prop k="arrow_width" v="0"/>
              <prop k="arrow_width_unit" v="MM"/>
              <prop k="arrow_width_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="head_length" v="1.5"/>
              <prop k="head_length_unit" v="MM"/>
              <prop k="head_length_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="head_thickness" v="1.5"/>
              <prop k="head_thickness_unit" v="MM"/>
              <prop k="head_thickness_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="head_type" v="2"/>
              <prop k="is_curved" v="1"/>
              <prop k="is_repeated" v="1"/>
              <prop k="offset" v="-5"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="ring_filter" v="0"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" value="" type="QString"/>
                  <Option name="properties"/>
                  <Option name="type" value="collection" type="QString"/>
                </Option>
              </data_defined_properties>
              <symbol name="@@2@0@0" alpha="1" force_rhr="0" clip_to_extent="1" type="fill">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" value="" type="QString"/>
                    <Option name="properties"/>
                    <Option name="type" value="collection" type="QString"/>
                  </Option>
                </data_defined_properties>
                <layer class="SimpleFill" locked="0" enabled="1" pass="0">
                  <Option type="Map">
                    <Option name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="color" value="31,31,31,255" type="QString"/>
                    <Option name="joinstyle" value="bevel" type="QString"/>
                    <Option name="offset" value="0,0" type="QString"/>
                    <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="offset_unit" value="MM" type="QString"/>
                    <Option name="outline_color" value="35,35,35,255" type="QString"/>
                    <Option name="outline_style" value="solid" type="QString"/>
                    <Option name="outline_width" value="0.26" type="QString"/>
                    <Option name="outline_width_unit" value="MM" type="QString"/>
                    <Option name="style" value="solid" type="QString"/>
                  </Option>
                  <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="31,31,31,255"/>
                  <prop k="joinstyle" v="bevel"/>
                  <prop k="offset" v="0,0"/>
                  <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="outline_color" v="35,35,35,255"/>
                  <prop k="outline_style" v="solid"/>
                  <prop k="outline_width" v="0.26"/>
                  <prop k="outline_width_unit" v="MM"/>
                  <prop k="style" v="solid"/>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" value="" type="QString"/>
                      <Option name="properties"/>
                      <Option name="type" value="collection" type="QString"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
            <layer class="MarkerLine" locked="0" enabled="1" pass="0">
              <Option type="Map">
                <Option name="average_angle_length" value="4" type="QString"/>
                <Option name="average_angle_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="average_angle_unit" value="MM" type="QString"/>
                <Option name="interval" value="3" type="QString"/>
                <Option name="interval_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="interval_unit" value="MM" type="QString"/>
                <Option name="offset" value="-5" type="QString"/>
                <Option name="offset_along_line" value="0" type="QString"/>
                <Option name="offset_along_line_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_along_line_unit" value="MM" type="QString"/>
                <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_unit" value="MM" type="QString"/>
                <Option name="placement" value="centralpoint" type="QString"/>
                <Option name="ring_filter" value="0" type="QString"/>
                <Option name="rotate" value="1" type="QString"/>
              </Option>
              <prop k="average_angle_length" v="4"/>
              <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="average_angle_unit" v="MM"/>
              <prop k="interval" v="3"/>
              <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="interval_unit" v="MM"/>
              <prop k="offset" v="-5"/>
              <prop k="offset_along_line" v="0"/>
              <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_along_line_unit" v="MM"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="placement" v="centralpoint"/>
              <prop k="ring_filter" v="0"/>
              <prop k="rotate" v="1"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" value="" type="QString"/>
                  <Option name="properties"/>
                  <Option name="type" value="collection" type="QString"/>
                </Option>
              </data_defined_properties>
              <symbol name="@@2@0@1" alpha="1" force_rhr="0" clip_to_extent="1" type="marker">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" value="" type="QString"/>
                    <Option name="properties"/>
                    <Option name="type" value="collection" type="QString"/>
                  </Option>
                </data_defined_properties>
                <layer class="FontMarker" locked="0" enabled="1" pass="0">
                  <Option type="Map">
                    <Option name="angle" value="0" type="QString"/>
                    <Option name="chr" value="A" type="QString"/>
                    <Option name="color" value="31,31,31,255" type="QString"/>
                    <Option name="font" value="Arial" type="QString"/>
                    <Option name="font_style" value="Normal" type="QString"/>
                    <Option name="horizontal_anchor_point" value="1" type="QString"/>
                    <Option name="joinstyle" value="bevel" type="QString"/>
                    <Option name="offset" value="0,6" type="QString"/>
                    <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="offset_unit" value="Point" type="QString"/>
                    <Option name="outline_color" value="35,35,35,255" type="QString"/>
                    <Option name="outline_width" value="0.2" type="QString"/>
                    <Option name="outline_width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="outline_width_unit" value="MM" type="QString"/>
                    <Option name="size" value="10" type="QString"/>
                    <Option name="size_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="size_unit" value="Point" type="QString"/>
                    <Option name="vertical_anchor_point" value="1" type="QString"/>
                  </Option>
                  <prop k="angle" v="0"/>
                  <prop k="chr" v="A"/>
                  <prop k="color" v="31,31,31,255"/>
                  <prop k="font" v="Arial"/>
                  <prop k="font_style" v="Normal"/>
                  <prop k="horizontal_anchor_point" v="1"/>
                  <prop k="joinstyle" v="bevel"/>
                  <prop k="offset" v="0,6"/>
                  <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="offset_unit" v="Point"/>
                  <prop k="outline_color" v="35,35,35,255"/>
                  <prop k="outline_width" v="0.2"/>
                  <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="outline_width_unit" v="MM"/>
                  <prop k="size" v="10"/>
                  <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="size_unit" v="Point"/>
                  <prop k="vertical_anchor_point" v="1"/>
                  <effect type="effectStack" enabled="1">
                    <effect type="dropShadow">
                      <Option type="Map">
                        <Option name="blend_mode" value="13" type="QString"/>
                        <Option name="blur_level" value="2.645" type="QString"/>
                        <Option name="blur_unit" value="MM" type="QString"/>
                        <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                        <Option name="color" value="0,0,0,255" type="QString"/>
                        <Option name="draw_mode" value="2" type="QString"/>
                        <Option name="enabled" value="0" type="QString"/>
                        <Option name="offset_angle" value="135" type="QString"/>
                        <Option name="offset_distance" value="2" type="QString"/>
                        <Option name="offset_unit" value="MM" type="QString"/>
                        <Option name="offset_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                        <Option name="opacity" value="1" type="QString"/>
                      </Option>
                      <prop k="blend_mode" v="13"/>
                      <prop k="blur_level" v="2.645"/>
                      <prop k="blur_unit" v="MM"/>
                      <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                      <prop k="color" v="0,0,0,255"/>
                      <prop k="draw_mode" v="2"/>
                      <prop k="enabled" v="0"/>
                      <prop k="offset_angle" v="135"/>
                      <prop k="offset_distance" v="2"/>
                      <prop k="offset_unit" v="MM"/>
                      <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                      <prop k="opacity" v="1"/>
                    </effect>
                    <effect type="outerGlow">
                      <Option type="Map">
                        <Option name="blend_mode" value="0" type="QString"/>
                        <Option name="blur_level" value="1" type="QString"/>
                        <Option name="blur_unit" value="MM" type="QString"/>
                        <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                        <Option name="color_type" value="0" type="QString"/>
                        <Option name="draw_mode" value="2" type="QString"/>
                        <Option name="enabled" value="1" type="QString"/>
                        <Option name="opacity" value="0.5" type="QString"/>
                        <Option name="single_color" value="255,255,255,255" type="QString"/>
                        <Option name="spread" value="3" type="QString"/>
                        <Option name="spread_unit" value="MM" type="QString"/>
                        <Option name="spread_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                      </Option>
                      <prop k="blend_mode" v="0"/>
                      <prop k="blur_level" v="1"/>
                      <prop k="blur_unit" v="MM"/>
                      <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                      <prop k="color_type" v="0"/>
                      <prop k="draw_mode" v="2"/>
                      <prop k="enabled" v="1"/>
                      <prop k="opacity" v="0.5"/>
                      <prop k="single_color" v="255,255,255,255"/>
                      <prop k="spread" v="3"/>
                      <prop k="spread_unit" v="MM"/>
                      <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                    </effect>
                    <effect type="drawSource">
                      <Option type="Map">
                        <Option name="blend_mode" value="0" type="QString"/>
                        <Option name="draw_mode" value="2" type="QString"/>
                        <Option name="enabled" value="1" type="QString"/>
                        <Option name="opacity" value="1" type="QString"/>
                      </Option>
                      <prop k="blend_mode" v="0"/>
                      <prop k="draw_mode" v="2"/>
                      <prop k="enabled" v="1"/>
                      <prop k="opacity" v="1"/>
                    </effect>
                    <effect type="innerShadow">
                      <Option type="Map">
                        <Option name="blend_mode" value="13" type="QString"/>
                        <Option name="blur_level" value="2.645" type="QString"/>
                        <Option name="blur_unit" value="MM" type="QString"/>
                        <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                        <Option name="color" value="0,0,0,255" type="QString"/>
                        <Option name="draw_mode" value="2" type="QString"/>
                        <Option name="enabled" value="0" type="QString"/>
                        <Option name="offset_angle" value="135" type="QString"/>
                        <Option name="offset_distance" value="2" type="QString"/>
                        <Option name="offset_unit" value="MM" type="QString"/>
                        <Option name="offset_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                        <Option name="opacity" value="1" type="QString"/>
                      </Option>
                      <prop k="blend_mode" v="13"/>
                      <prop k="blur_level" v="2.645"/>
                      <prop k="blur_unit" v="MM"/>
                      <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                      <prop k="color" v="0,0,0,255"/>
                      <prop k="draw_mode" v="2"/>
                      <prop k="enabled" v="0"/>
                      <prop k="offset_angle" v="135"/>
                      <prop k="offset_distance" v="2"/>
                      <prop k="offset_unit" v="MM"/>
                      <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                      <prop k="opacity" v="1"/>
                    </effect>
                    <effect type="innerGlow">
                      <Option type="Map">
                        <Option name="blend_mode" value="0" type="QString"/>
                        <Option name="blur_level" value="2.645" type="QString"/>
                        <Option name="blur_unit" value="MM" type="QString"/>
                        <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                        <Option name="color_type" value="0" type="QString"/>
                        <Option name="draw_mode" value="2" type="QString"/>
                        <Option name="enabled" value="0" type="QString"/>
                        <Option name="opacity" value="0.5" type="QString"/>
                        <Option name="single_color" value="255,255,255,255" type="QString"/>
                        <Option name="spread" value="2" type="QString"/>
                        <Option name="spread_unit" value="MM" type="QString"/>
                        <Option name="spread_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                      </Option>
                      <prop k="blend_mode" v="0"/>
                      <prop k="blur_level" v="2.645"/>
                      <prop k="blur_unit" v="MM"/>
                      <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                      <prop k="color_type" v="0"/>
                      <prop k="draw_mode" v="2"/>
                      <prop k="enabled" v="0"/>
                      <prop k="opacity" v="0.5"/>
                      <prop k="single_color" v="255,255,255,255"/>
                      <prop k="spread" v="2"/>
                      <prop k="spread_unit" v="MM"/>
                      <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                    </effect>
                  </effect>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" value="" type="QString"/>
                      <Option name="properties" type="Map">
                        <Option name="char" type="Map">
                          <Option name="active" value="true" type="bool"/>
                          <Option name="expression" value="'Az '  || &#xd;&#xa;dd2dms(&#xd;&#xa;degrees(  &#xd;&#xa;azimuth(&#xd;&#xa;start_point(geometry_n(  $geometry,  @geometry_part_num )), end_point(geometry_n(  $geometry,  @geometry_part_num ))))&#xd;&#xa;,0)" type="QString"/>
                          <Option name="type" value="3" type="int"/>
                        </Option>
                      </Option>
                      <Option name="type" value="collection" type="QString"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
            <layer class="SimpleLine" locked="0" enabled="1" pass="0">
              <Option type="Map">
                <Option name="align_dash_pattern" value="0" type="QString"/>
                <Option name="capstyle" value="square" type="QString"/>
                <Option name="customdash" value="5;2" type="QString"/>
                <Option name="customdash_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="customdash_unit" value="MM" type="QString"/>
                <Option name="dash_pattern_offset" value="0" type="QString"/>
                <Option name="dash_pattern_offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="dash_pattern_offset_unit" value="MM" type="QString"/>
                <Option name="draw_inside_polygon" value="0" type="QString"/>
                <Option name="joinstyle" value="bevel" type="QString"/>
                <Option name="line_color" value="35,35,35,255" type="QString"/>
                <Option name="line_style" value="solid" type="QString"/>
                <Option name="line_width" value="0.4" type="QString"/>
                <Option name="line_width_unit" value="MM" type="QString"/>
                <Option name="offset" value="-5" type="QString"/>
                <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_unit" value="MM" type="QString"/>
                <Option name="ring_filter" value="0" type="QString"/>
                <Option name="trim_distance_end" value="0" type="QString"/>
                <Option name="trim_distance_end_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="trim_distance_end_unit" value="MM" type="QString"/>
                <Option name="trim_distance_start" value="0" type="QString"/>
                <Option name="trim_distance_start_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="trim_distance_start_unit" value="MM" type="QString"/>
                <Option name="tweak_dash_pattern_on_corners" value="0" type="QString"/>
                <Option name="use_custom_dash" value="0" type="QString"/>
                <Option name="width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="square"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="line_color" v="35,35,35,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="0.4"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="-5"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" value="" type="QString"/>
                  <Option name="properties"/>
                  <Option name="type" value="collection" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
            <layer class="MarkerLine" locked="0" enabled="1" pass="0">
              <Option type="Map">
                <Option name="average_angle_length" value="4" type="QString"/>
                <Option name="average_angle_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="average_angle_unit" value="MM" type="QString"/>
                <Option name="interval" value="3" type="QString"/>
                <Option name="interval_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="interval_unit" value="MM" type="QString"/>
                <Option name="offset" value="-5" type="QString"/>
                <Option name="offset_along_line" value="0" type="QString"/>
                <Option name="offset_along_line_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_along_line_unit" value="MM" type="QString"/>
                <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_unit" value="MM" type="QString"/>
                <Option name="placement" value="vertex" type="QString"/>
                <Option name="ring_filter" value="0" type="QString"/>
                <Option name="rotate" value="1" type="QString"/>
              </Option>
              <prop k="average_angle_length" v="4"/>
              <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="average_angle_unit" v="MM"/>
              <prop k="interval" v="3"/>
              <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="interval_unit" v="MM"/>
              <prop k="offset" v="-5"/>
              <prop k="offset_along_line" v="0"/>
              <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_along_line_unit" v="MM"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="placement" v="vertex"/>
              <prop k="ring_filter" v="0"/>
              <prop k="rotate" v="1"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" value="" type="QString"/>
                  <Option name="properties"/>
                  <Option name="type" value="collection" type="QString"/>
                </Option>
              </data_defined_properties>
              <symbol name="@@2@0@3" alpha="1" force_rhr="0" clip_to_extent="1" type="marker">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" value="" type="QString"/>
                    <Option name="properties"/>
                    <Option name="type" value="collection" type="QString"/>
                  </Option>
                </data_defined_properties>
                <layer class="SimpleMarker" locked="0" enabled="1" pass="0">
                  <Option type="Map">
                    <Option name="angle" value="0" type="QString"/>
                    <Option name="cap_style" value="square" type="QString"/>
                    <Option name="color" value="255,0,0,255" type="QString"/>
                    <Option name="horizontal_anchor_point" value="1" type="QString"/>
                    <Option name="joinstyle" value="bevel" type="QString"/>
                    <Option name="name" value="line" type="QString"/>
                    <Option name="offset" value="0,0" type="QString"/>
                    <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="offset_unit" value="MM" type="QString"/>
                    <Option name="outline_color" value="35,35,35,255" type="QString"/>
                    <Option name="outline_style" value="solid" type="QString"/>
                    <Option name="outline_width" value="0.3" type="QString"/>
                    <Option name="outline_width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="outline_width_unit" value="MM" type="QString"/>
                    <Option name="scale_method" value="diameter" type="QString"/>
                    <Option name="size" value="10" type="QString"/>
                    <Option name="size_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="size_unit" value="MM" type="QString"/>
                    <Option name="vertical_anchor_point" value="1" type="QString"/>
                  </Option>
                  <prop k="angle" v="0"/>
                  <prop k="cap_style" v="square"/>
                  <prop k="color" v="255,0,0,255"/>
                  <prop k="horizontal_anchor_point" v="1"/>
                  <prop k="joinstyle" v="bevel"/>
                  <prop k="name" v="line"/>
                  <prop k="offset" v="0,0"/>
                  <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="outline_color" v="35,35,35,255"/>
                  <prop k="outline_style" v="solid"/>
                  <prop k="outline_width" v="0.3"/>
                  <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="outline_width_unit" v="MM"/>
                  <prop k="scale_method" v="diameter"/>
                  <prop k="size" v="10"/>
                  <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="size_unit" v="MM"/>
                  <prop k="vertical_anchor_point" v="1"/>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" value="" type="QString"/>
                      <Option name="properties"/>
                      <Option name="type" value="collection" type="QString"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="3" alpha="1" force_rhr="0" clip_to_extent="1" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" value="" type="QString"/>
            <Option name="properties"/>
            <Option name="type" value="collection" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleFill" locked="0" enabled="1" pass="0">
          <Option type="Map">
            <Option name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
            <Option name="color" value="235,176,121,111" type="QString"/>
            <Option name="joinstyle" value="bevel" type="QString"/>
            <Option name="offset" value="0,0" type="QString"/>
            <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
            <Option name="offset_unit" value="MM" type="QString"/>
            <Option name="outline_color" value="35,35,35,255" type="QString"/>
            <Option name="outline_style" value="solid" type="QString"/>
            <Option name="outline_width" value="0.3" type="QString"/>
            <Option name="outline_width_unit" value="MM" type="QString"/>
            <Option name="style" value="solid" type="QString"/>
          </Option>
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="235,176,121,111"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.3"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" value="" type="QString"/>
              <Option name="properties"/>
              <Option name="type" value="collection" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style allowHtml="0" useSubstitutions="0" namedStyle="Bold" fontStrikeout="0" textOpacity="1" textOrientation="horizontal" isExpression="1" blendMode="0" fontSize="12" multilineHeight="1" previewBkgrdColor="255,255,255,255" fontUnderline="0" capitalization="0" fontWeight="75" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fieldName="format_number(area($geometry),2)  ||  ' m²'" fontLetterSpacing="0" fontKerning="1" fontWordSpacing="0" legendString="Aa" fontFamily="Liberation Sans" fontSizeUnit="Point" textColor="255,255,255,255" fontItalic="0">
        <families/>
        <text-buffer bufferNoFill="1" bufferColor="31,31,31,255" bufferOpacity="0.48100000000000004" bufferJoinStyle="128" bufferBlendMode="0" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferDraw="1" bufferSize="0.5" bufferSizeUnits="MM">
          <effect type="effectStack" enabled="1">
            <effect type="dropShadow">
              <Option type="Map">
                <Option name="blend_mode" value="13" type="QString"/>
                <Option name="blur_level" value="2.645" type="QString"/>
                <Option name="blur_unit" value="MM" type="QString"/>
                <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="color" value="0,0,0,255" type="QString"/>
                <Option name="draw_mode" value="2" type="QString"/>
                <Option name="enabled" value="0" type="QString"/>
                <Option name="offset_angle" value="135" type="QString"/>
                <Option name="offset_distance" value="2" type="QString"/>
                <Option name="offset_unit" value="MM" type="QString"/>
                <Option name="offset_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="opacity" value="1" type="QString"/>
              </Option>
              <prop k="blend_mode" v="13"/>
              <prop k="blur_level" v="2.645"/>
              <prop k="blur_unit" v="MM"/>
              <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="color" v="0,0,0,255"/>
              <prop k="draw_mode" v="2"/>
              <prop k="enabled" v="0"/>
              <prop k="offset_angle" v="135"/>
              <prop k="offset_distance" v="2"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="opacity" v="1"/>
            </effect>
            <effect type="outerGlow">
              <Option type="Map">
                <Option name="blend_mode" value="0" type="QString"/>
                <Option name="blur_level" value="1" type="QString"/>
                <Option name="blur_unit" value="MM" type="QString"/>
                <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="color1" value="48,18,59,255" type="QString"/>
                <Option name="color2" value="122,4,3,255" type="QString"/>
                <Option name="color_type" value="1" type="QString"/>
                <Option name="discrete" value="0" type="QString"/>
                <Option name="draw_mode" value="2" type="QString"/>
                <Option name="enabled" value="1" type="QString"/>
                <Option name="opacity" value="0.5" type="QString"/>
                <Option name="rampType" value="gradient" type="QString"/>
                <Option name="single_color" value="255,255,255,255" type="QString"/>
                <Option name="spread" value="3" type="QString"/>
                <Option name="spread_unit" value="MM" type="QString"/>
                <Option name="spread_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="stops" value="0.0039063;50,21,67,255:0.0078125;51,24,74,255:0.0117188;52,27,81,255:0.015625;53,30,88,255:0.0195313;54,33,95,255:0.0234375;55,36,102,255:0.0273438;56,39,109,255:0.03125;57,42,115,255:0.0351563;58,45,121,255:0.0390625;59,47,128,255:0.0429688;60,50,134,255:0.046875;61,53,139,255:0.0507813;62,56,145,255:0.0546875;63,59,151,255:0.0585938;63,62,156,255:0.0625;64,64,162,255:0.0664063;65,67,167,255:0.0703125;65,70,172,255:0.0742188;66,73,177,255:0.078125;66,75,181,255:0.0820313;67,78,186,255:0.0859375;68,81,191,255:0.0898438;68,84,195,255:0.09375;68,86,199,255:0.0976563;69,89,203,255:0.101563;69,92,207,255:0.105469;69,94,211,255:0.109375;70,97,214,255:0.113281;70,100,218,255:0.117188;70,102,221,255:0.121094;70,105,224,255:0.125;70,107,227,255:0.128906;71,110,230,255:0.132813;71,113,233,255:0.136719;71,115,235,255:0.140625;71,118,238,255:0.144531;71,120,240,255:0.148438;71,123,242,255:0.152344;70,125,244,255:0.15625;70,128,246,255:0.160156;70,130,248,255:0.164063;70,133,250,255:0.167969;70,135,251,255:0.171875;69,138,252,255:0.175781;69,140,253,255:0.179688;68,143,254,255:0.183594;67,145,254,255:0.1875;66,148,255,255:0.191406;65,150,255,255:0.195313;64,153,255,255:0.199219;62,155,254,255:0.203125;61,158,254,255:0.207031;59,160,253,255:0.210938;58,163,252,255:0.214844;56,165,251,255:0.21875;55,168,250,255:0.222656;53,171,248,255:0.226563;51,173,247,255:0.230469;49,175,245,255:0.234375;47,178,244,255:0.238281;46,180,242,255:0.242188;44,183,240,255:0.246094;42,185,238,255:0.25;40,188,235,255:0.253906;39,190,233,255:0.257813;37,192,231,255:0.261719;35,195,228,255:0.265625;34,197,226,255:0.269531;32,199,223,255:0.273438;31,201,221,255:0.277344;30,203,218,255:0.28125;28,205,216,255:0.285156;27,208,213,255:0.289063;26,210,210,255:0.292969;26,212,208,255:0.296875;25,213,205,255:0.300781;24,215,202,255:0.304688;24,217,200,255:0.308594;24,219,197,255:0.3125;24,221,194,255:0.316406;24,222,192,255:0.320313;24,224,189,255:0.324219;25,226,187,255:0.328125;25,227,185,255:0.332031;26,228,182,255:0.335938;28,230,180,255:0.339844;29,231,178,255:0.34375;31,233,175,255:0.347656;32,234,172,255:0.351563;34,235,170,255:0.355469;37,236,167,255:0.359375;39,238,164,255:0.363281;42,239,161,255:0.367188;44,240,158,255:0.371094;47,241,155,255:0.375;50,242,152,255:0.378906;53,243,148,255:0.382813;56,244,145,255:0.386719;60,245,142,255:0.390625;63,246,138,255:0.394531;67,247,135,255:0.398438;70,248,132,255:0.402344;74,248,128,255:0.40625;78,249,125,255:0.410156;82,250,122,255:0.414063;85,250,118,255:0.417969;89,251,115,255:0.421875;93,252,111,255:0.425781;97,252,108,255:0.429688;101,253,105,255:0.433594;105,253,102,255:0.4375;109,254,98,255:0.441406;113,254,95,255:0.445313;117,254,92,255:0.449219;121,254,89,255:0.453125;125,255,86,255:0.457031;128,255,83,255:0.460938;132,255,81,255:0.464844;136,255,78,255:0.46875;139,255,75,255:0.472656;143,255,73,255:0.476563;146,255,71,255:0.480469;150,254,68,255:0.484375;153,254,66,255:0.488281;156,254,64,255:0.492188;159,253,63,255:0.496094;161,253,61,255:0.5;164,252,60,255:0.503906;167,252,58,255:0.507813;169,251,57,255:0.511719;172,251,56,255:0.515625;175,250,55,255:0.519531;177,249,54,255:0.523438;180,248,54,255:0.527344;183,247,53,255:0.53125;185,246,53,255:0.535156;188,245,52,255:0.539063;190,244,52,255:0.542969;193,243,52,255:0.546875;195,241,52,255:0.550781;198,240,52,255:0.554688;200,239,52,255:0.558594;203,237,52,255:0.5625;205,236,52,255:0.566406;208,234,52,255:0.570313;210,233,53,255:0.574219;212,231,53,255:0.578125;215,229,53,255:0.582031;217,228,54,255:0.585938;219,226,54,255:0.589844;221,224,55,255:0.59375;223,223,55,255:0.597656;225,221,55,255:0.601563;227,219,56,255:0.605469;229,217,56,255:0.609375;231,215,57,255:0.613281;233,213,57,255:0.617188;235,211,57,255:0.621094;236,209,58,255:0.625;238,207,58,255:0.628906;239,205,58,255:0.632813;241,203,58,255:0.636719;242,201,58,255:0.640625;244,199,58,255:0.644531;245,197,58,255:0.648438;246,195,58,255:0.652344;247,193,58,255:0.65625;248,190,57,255:0.660156;249,188,57,255:0.664063;250,186,57,255:0.667969;251,184,56,255:0.671875;251,182,55,255:0.675781;252,179,54,255:0.679688;252,177,54,255:0.683594;253,174,53,255:0.6875;253,172,52,255:0.691406;254,169,51,255:0.695313;254,167,50,255:0.699219;254,164,49,255:0.703125;254,161,48,255:0.707031;254,158,47,255:0.710938;254,155,45,255:0.714844;254,153,44,255:0.71875;254,150,43,255:0.722656;254,147,42,255:0.726563;254,144,41,255:0.730469;253,141,39,255:0.734375;253,138,38,255:0.738281;252,135,37,255:0.742188;252,132,35,255:0.746094;251,129,34,255:0.75;251,126,33,255:0.753906;250,123,31,255:0.757813;249,120,30,255:0.761719;249,117,29,255:0.765625;248,114,28,255:0.769531;247,111,26,255:0.773438;246,108,25,255:0.777344;245,105,24,255:0.78125;244,102,23,255:0.785156;243,99,21,255:0.789063;242,96,20,255:0.792969;241,93,19,255:0.796875;240,91,18,255:0.800781;239,88,17,255:0.804688;237,85,16,255:0.808594;236,83,15,255:0.8125;235,80,14,255:0.816406;234,78,13,255:0.820313;232,75,12,255:0.824219;231,73,12,255:0.828125;229,71,11,255:0.832031;228,69,10,255:0.835938;226,67,10,255:0.839844;225,65,9,255:0.84375;223,63,8,255:0.847656;221,61,8,255:0.851563;220,59,7,255:0.855469;218,57,7,255:0.859375;216,55,6,255:0.863281;214,53,6,255:0.867188;212,51,5,255:0.871094;210,49,5,255:0.875;208,47,5,255:0.878906;206,45,4,255:0.882813;204,43,4,255:0.886719;202,42,4,255:0.890625;200,40,3,255:0.894531;197,38,3,255:0.898438;195,37,3,255:0.902344;193,35,2,255:0.90625;190,33,2,255:0.910156;188,32,2,255:0.914063;185,30,2,255:0.917969;183,29,2,255:0.921875;180,27,1,255:0.925781;178,26,1,255:0.929688;175,24,1,255:0.933594;172,23,1,255:0.9375;169,22,1,255:0.941406;167,20,1,255:0.945313;164,19,1,255:0.949219;161,18,1,255:0.953125;158,16,1,255:0.957031;155,15,1,255:0.960938;152,14,1,255:0.964844;149,13,1,255:0.96875;146,11,1,255:0.972656;142,10,1,255:0.976563;139,9,2,255:0.980469;136,8,2,255:0.984375;133,7,2,255:0.988281;129,6,2,255" type="QString"/>
              </Option>
              <prop k="blend_mode" v="0"/>
              <prop k="blur_level" v="1"/>
              <prop k="blur_unit" v="MM"/>
              <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="color1" v="48,18,59,255"/>
              <prop k="color2" v="122,4,3,255"/>
              <prop k="color_type" v="1"/>
              <prop k="discrete" v="0"/>
              <prop k="draw_mode" v="2"/>
              <prop k="enabled" v="1"/>
              <prop k="opacity" v="0.5"/>
              <prop k="rampType" v="gradient"/>
              <prop k="single_color" v="255,255,255,255"/>
              <prop k="spread" v="3"/>
              <prop k="spread_unit" v="MM"/>
              <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="stops" v="0.0039063;50,21,67,255:0.0078125;51,24,74,255:0.0117188;52,27,81,255:0.015625;53,30,88,255:0.0195313;54,33,95,255:0.0234375;55,36,102,255:0.0273438;56,39,109,255:0.03125;57,42,115,255:0.0351563;58,45,121,255:0.0390625;59,47,128,255:0.0429688;60,50,134,255:0.046875;61,53,139,255:0.0507813;62,56,145,255:0.0546875;63,59,151,255:0.0585938;63,62,156,255:0.0625;64,64,162,255:0.0664063;65,67,167,255:0.0703125;65,70,172,255:0.0742188;66,73,177,255:0.078125;66,75,181,255:0.0820313;67,78,186,255:0.0859375;68,81,191,255:0.0898438;68,84,195,255:0.09375;68,86,199,255:0.0976563;69,89,203,255:0.101563;69,92,207,255:0.105469;69,94,211,255:0.109375;70,97,214,255:0.113281;70,100,218,255:0.117188;70,102,221,255:0.121094;70,105,224,255:0.125;70,107,227,255:0.128906;71,110,230,255:0.132813;71,113,233,255:0.136719;71,115,235,255:0.140625;71,118,238,255:0.144531;71,120,240,255:0.148438;71,123,242,255:0.152344;70,125,244,255:0.15625;70,128,246,255:0.160156;70,130,248,255:0.164063;70,133,250,255:0.167969;70,135,251,255:0.171875;69,138,252,255:0.175781;69,140,253,255:0.179688;68,143,254,255:0.183594;67,145,254,255:0.1875;66,148,255,255:0.191406;65,150,255,255:0.195313;64,153,255,255:0.199219;62,155,254,255:0.203125;61,158,254,255:0.207031;59,160,253,255:0.210938;58,163,252,255:0.214844;56,165,251,255:0.21875;55,168,250,255:0.222656;53,171,248,255:0.226563;51,173,247,255:0.230469;49,175,245,255:0.234375;47,178,244,255:0.238281;46,180,242,255:0.242188;44,183,240,255:0.246094;42,185,238,255:0.25;40,188,235,255:0.253906;39,190,233,255:0.257813;37,192,231,255:0.261719;35,195,228,255:0.265625;34,197,226,255:0.269531;32,199,223,255:0.273438;31,201,221,255:0.277344;30,203,218,255:0.28125;28,205,216,255:0.285156;27,208,213,255:0.289063;26,210,210,255:0.292969;26,212,208,255:0.296875;25,213,205,255:0.300781;24,215,202,255:0.304688;24,217,200,255:0.308594;24,219,197,255:0.3125;24,221,194,255:0.316406;24,222,192,255:0.320313;24,224,189,255:0.324219;25,226,187,255:0.328125;25,227,185,255:0.332031;26,228,182,255:0.335938;28,230,180,255:0.339844;29,231,178,255:0.34375;31,233,175,255:0.347656;32,234,172,255:0.351563;34,235,170,255:0.355469;37,236,167,255:0.359375;39,238,164,255:0.363281;42,239,161,255:0.367188;44,240,158,255:0.371094;47,241,155,255:0.375;50,242,152,255:0.378906;53,243,148,255:0.382813;56,244,145,255:0.386719;60,245,142,255:0.390625;63,246,138,255:0.394531;67,247,135,255:0.398438;70,248,132,255:0.402344;74,248,128,255:0.40625;78,249,125,255:0.410156;82,250,122,255:0.414063;85,250,118,255:0.417969;89,251,115,255:0.421875;93,252,111,255:0.425781;97,252,108,255:0.429688;101,253,105,255:0.433594;105,253,102,255:0.4375;109,254,98,255:0.441406;113,254,95,255:0.445313;117,254,92,255:0.449219;121,254,89,255:0.453125;125,255,86,255:0.457031;128,255,83,255:0.460938;132,255,81,255:0.464844;136,255,78,255:0.46875;139,255,75,255:0.472656;143,255,73,255:0.476563;146,255,71,255:0.480469;150,254,68,255:0.484375;153,254,66,255:0.488281;156,254,64,255:0.492188;159,253,63,255:0.496094;161,253,61,255:0.5;164,252,60,255:0.503906;167,252,58,255:0.507813;169,251,57,255:0.511719;172,251,56,255:0.515625;175,250,55,255:0.519531;177,249,54,255:0.523438;180,248,54,255:0.527344;183,247,53,255:0.53125;185,246,53,255:0.535156;188,245,52,255:0.539063;190,244,52,255:0.542969;193,243,52,255:0.546875;195,241,52,255:0.550781;198,240,52,255:0.554688;200,239,52,255:0.558594;203,237,52,255:0.5625;205,236,52,255:0.566406;208,234,52,255:0.570313;210,233,53,255:0.574219;212,231,53,255:0.578125;215,229,53,255:0.582031;217,228,54,255:0.585938;219,226,54,255:0.589844;221,224,55,255:0.59375;223,223,55,255:0.597656;225,221,55,255:0.601563;227,219,56,255:0.605469;229,217,56,255:0.609375;231,215,57,255:0.613281;233,213,57,255:0.617188;235,211,57,255:0.621094;236,209,58,255:0.625;238,207,58,255:0.628906;239,205,58,255:0.632813;241,203,58,255:0.636719;242,201,58,255:0.640625;244,199,58,255:0.644531;245,197,58,255:0.648438;246,195,58,255:0.652344;247,193,58,255:0.65625;248,190,57,255:0.660156;249,188,57,255:0.664063;250,186,57,255:0.667969;251,184,56,255:0.671875;251,182,55,255:0.675781;252,179,54,255:0.679688;252,177,54,255:0.683594;253,174,53,255:0.6875;253,172,52,255:0.691406;254,169,51,255:0.695313;254,167,50,255:0.699219;254,164,49,255:0.703125;254,161,48,255:0.707031;254,158,47,255:0.710938;254,155,45,255:0.714844;254,153,44,255:0.71875;254,150,43,255:0.722656;254,147,42,255:0.726563;254,144,41,255:0.730469;253,141,39,255:0.734375;253,138,38,255:0.738281;252,135,37,255:0.742188;252,132,35,255:0.746094;251,129,34,255:0.75;251,126,33,255:0.753906;250,123,31,255:0.757813;249,120,30,255:0.761719;249,117,29,255:0.765625;248,114,28,255:0.769531;247,111,26,255:0.773438;246,108,25,255:0.777344;245,105,24,255:0.78125;244,102,23,255:0.785156;243,99,21,255:0.789063;242,96,20,255:0.792969;241,93,19,255:0.796875;240,91,18,255:0.800781;239,88,17,255:0.804688;237,85,16,255:0.808594;236,83,15,255:0.8125;235,80,14,255:0.816406;234,78,13,255:0.820313;232,75,12,255:0.824219;231,73,12,255:0.828125;229,71,11,255:0.832031;228,69,10,255:0.835938;226,67,10,255:0.839844;225,65,9,255:0.84375;223,63,8,255:0.847656;221,61,8,255:0.851563;220,59,7,255:0.855469;218,57,7,255:0.859375;216,55,6,255:0.863281;214,53,6,255:0.867188;212,51,5,255:0.871094;210,49,5,255:0.875;208,47,5,255:0.878906;206,45,4,255:0.882813;204,43,4,255:0.886719;202,42,4,255:0.890625;200,40,3,255:0.894531;197,38,3,255:0.898438;195,37,3,255:0.902344;193,35,2,255:0.90625;190,33,2,255:0.910156;188,32,2,255:0.914063;185,30,2,255:0.917969;183,29,2,255:0.921875;180,27,1,255:0.925781;178,26,1,255:0.929688;175,24,1,255:0.933594;172,23,1,255:0.9375;169,22,1,255:0.941406;167,20,1,255:0.945313;164,19,1,255:0.949219;161,18,1,255:0.953125;158,16,1,255:0.957031;155,15,1,255:0.960938;152,14,1,255:0.964844;149,13,1,255:0.96875;146,11,1,255:0.972656;142,10,1,255:0.976563;139,9,2,255:0.980469;136,8,2,255:0.984375;133,7,2,255:0.988281;129,6,2,255"/>
            </effect>
            <effect type="drawSource">
              <Option type="Map">
                <Option name="blend_mode" value="0" type="QString"/>
                <Option name="draw_mode" value="2" type="QString"/>
                <Option name="enabled" value="1" type="QString"/>
                <Option name="opacity" value="1" type="QString"/>
              </Option>
              <prop k="blend_mode" v="0"/>
              <prop k="draw_mode" v="2"/>
              <prop k="enabled" v="1"/>
              <prop k="opacity" v="1"/>
            </effect>
            <effect type="innerShadow">
              <Option type="Map">
                <Option name="blend_mode" value="13" type="QString"/>
                <Option name="blur_level" value="2.645" type="QString"/>
                <Option name="blur_unit" value="MM" type="QString"/>
                <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="color" value="0,0,0,255" type="QString"/>
                <Option name="draw_mode" value="2" type="QString"/>
                <Option name="enabled" value="0" type="QString"/>
                <Option name="offset_angle" value="135" type="QString"/>
                <Option name="offset_distance" value="2" type="QString"/>
                <Option name="offset_unit" value="MM" type="QString"/>
                <Option name="offset_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="opacity" value="1" type="QString"/>
              </Option>
              <prop k="blend_mode" v="13"/>
              <prop k="blur_level" v="2.645"/>
              <prop k="blur_unit" v="MM"/>
              <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="color" v="0,0,0,255"/>
              <prop k="draw_mode" v="2"/>
              <prop k="enabled" v="0"/>
              <prop k="offset_angle" v="135"/>
              <prop k="offset_distance" v="2"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="opacity" v="1"/>
            </effect>
            <effect type="innerGlow">
              <Option type="Map">
                <Option name="blend_mode" value="0" type="QString"/>
                <Option name="blur_level" value="2.645" type="QString"/>
                <Option name="blur_unit" value="MM" type="QString"/>
                <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="color_type" value="0" type="QString"/>
                <Option name="draw_mode" value="2" type="QString"/>
                <Option name="enabled" value="0" type="QString"/>
                <Option name="opacity" value="0.5" type="QString"/>
                <Option name="single_color" value="255,255,255,255" type="QString"/>
                <Option name="spread" value="2" type="QString"/>
                <Option name="spread_unit" value="MM" type="QString"/>
                <Option name="spread_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
              </Option>
              <prop k="blend_mode" v="0"/>
              <prop k="blur_level" v="2.645"/>
              <prop k="blur_unit" v="MM"/>
              <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="color_type" v="0"/>
              <prop k="draw_mode" v="2"/>
              <prop k="enabled" v="0"/>
              <prop k="opacity" v="0.5"/>
              <prop k="single_color" v="255,255,255,255"/>
              <prop k="spread" v="2"/>
              <prop k="spread_unit" v="MM"/>
              <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
            </effect>
          </effect>
        </text-buffer>
        <text-mask maskSizeUnits="MM" maskOpacity="1" maskSize="0" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskType="0" maskJoinStyle="128" maskEnabled="0" maskedSymbolLayers=""/>
        <background shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeRotationType="0" shapeSizeUnit="Point" shapeOpacity="1" shapeBorderWidth="0" shapeBlendMode="0" shapeSVGFile="" shapeFillColor="255,255,255,255" shapeSizeX="0" shapeBorderWidthUnit="Point" shapeSizeType="0" shapeJoinStyle="64" shapeOffsetX="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeType="0" shapeBorderColor="128,128,128,255" shapeDraw="0" shapeSizeY="0" shapeRadiiX="0" shapeRotation="0" shapeRadiiUnit="Point" shapeOffsetUnit="Point" shapeOffsetY="0" shapeRadiiY="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0">
          <symbol name="markerSymbol" alpha="1" force_rhr="0" clip_to_extent="1" type="marker">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" value="" type="QString"/>
                <Option name="properties"/>
                <Option name="type" value="collection" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleMarker" locked="0" enabled="1" pass="0">
              <Option type="Map">
                <Option name="angle" value="0" type="QString"/>
                <Option name="cap_style" value="square" type="QString"/>
                <Option name="color" value="152,125,183,255" type="QString"/>
                <Option name="horizontal_anchor_point" value="1" type="QString"/>
                <Option name="joinstyle" value="bevel" type="QString"/>
                <Option name="name" value="circle" type="QString"/>
                <Option name="offset" value="0,0" type="QString"/>
                <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_unit" value="MM" type="QString"/>
                <Option name="outline_color" value="35,35,35,255" type="QString"/>
                <Option name="outline_style" value="solid" type="QString"/>
                <Option name="outline_width" value="0" type="QString"/>
                <Option name="outline_width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="outline_width_unit" value="MM" type="QString"/>
                <Option name="scale_method" value="diameter" type="QString"/>
                <Option name="size" value="2" type="QString"/>
                <Option name="size_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="size_unit" value="MM" type="QString"/>
                <Option name="vertical_anchor_point" value="1" type="QString"/>
              </Option>
              <prop k="angle" v="0"/>
              <prop k="cap_style" v="square"/>
              <prop k="color" v="152,125,183,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="circle"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="scale_method" v="diameter"/>
              <prop k="size" v="2"/>
              <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="size_unit" v="MM"/>
              <prop k="vertical_anchor_point" v="1"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" value="" type="QString"/>
                  <Option name="properties"/>
                  <Option name="type" value="collection" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
          <symbol name="fillSymbol" alpha="1" force_rhr="0" clip_to_extent="1" type="fill">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" value="" type="QString"/>
                <Option name="properties"/>
                <Option name="type" value="collection" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleFill" locked="0" enabled="1" pass="0">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="color" value="255,255,255,255" type="QString"/>
                <Option name="joinstyle" value="bevel" type="QString"/>
                <Option name="offset" value="0,0" type="QString"/>
                <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_unit" value="MM" type="QString"/>
                <Option name="outline_color" value="128,128,128,255" type="QString"/>
                <Option name="outline_style" value="no" type="QString"/>
                <Option name="outline_width" value="0" type="QString"/>
                <Option name="outline_width_unit" value="Point" type="QString"/>
                <Option name="style" value="solid" type="QString"/>
              </Option>
              <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="color" v="255,255,255,255"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="128,128,128,255"/>
              <prop k="outline_style" v="no"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_unit" v="Point"/>
              <prop k="style" v="solid"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" value="" type="QString"/>
                  <Option name="properties"/>
                  <Option name="type" value="collection" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </background>
        <shadow shadowOffsetDist="1" shadowOffsetGlobal="1" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowBlendMode="6" shadowOffsetAngle="135" shadowDraw="0" shadowOffsetUnit="MM" shadowUnder="0" shadowRadius="1.5" shadowRadiusUnit="MM" shadowOpacity="0.69999999999999996" shadowScale="100" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowColor="0,0,0,255" shadowRadiusAlphaOnly="0"/>
        <dd_properties>
          <Option type="Map">
            <Option name="name" value="" type="QString"/>
            <Option name="properties"/>
            <Option name="type" value="collection" type="QString"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format wrapChar="" autoWrapLength="0" reverseDirectionSymbol="0" plussign="0" useMaxLineLengthForAutoWrap="1" formatNumbers="0" rightDirectionSymbol=">" placeDirectionSymbol="0" multilineAlign="3" addDirectionSymbol="0" leftDirectionSymbol="&lt;" decimals="3"/>
      <placement labelOffsetMapUnitScale="3x:0,0,0,0,0,0" geometryGenerator="" distUnits="MM" yOffset="0" offsetType="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" lineAnchorPercent="0.5" xOffset="0" rotationAngle="0" polygonPlacementFlags="2" lineAnchorClipping="0" fitInPolygonOnly="0" repeatDistanceUnits="MM" geometryGeneratorEnabled="0" offsetUnits="MM" lineAnchorType="0" placement="0" priority="5" overrunDistanceUnit="MM" geometryGeneratorType="PointGeometry" placementFlags="10" repeatDistance="0" dist="0" distMapUnitScale="3x:0,0,0,0,0,0" rotationUnit="AngleDegrees" layerType="PolygonGeometry" maxCurvedCharAngleIn="25" preserveRotation="1" overrunDistance="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" maxCurvedCharAngleOut="-25" centroidInside="0" centroidWhole="0" quadOffset="4" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0"/>
      <rendering drawLabels="1" obstacleType="1" scaleMin="0" displayAll="0" obstacleFactor="1" limitNumLabels="0" upsidedownLabels="0" scaleMax="0" zIndex="0" minFeatureSize="0" obstacle="1" mergeLines="0" labelPerPart="0" maxNumLabels="2000" scaleVisibility="0" fontLimitPixelSize="0" fontMaxPixelSize="10000" fontMinPixelSize="3" unplacedVisibility="0"/>
      <dd_properties>
        <Option type="Map">
          <Option name="name" value="" type="QString"/>
          <Option name="properties"/>
          <Option name="type" value="collection" type="QString"/>
        </Option>
      </dd_properties>
      <callout type="simple">
        <Option type="Map">
          <Option name="anchorPoint" value="pole_of_inaccessibility" type="QString"/>
          <Option name="blendMode" value="0" type="int"/>
          <Option name="ddProperties" type="Map">
            <Option name="name" value="" type="QString"/>
            <Option name="properties"/>
            <Option name="type" value="collection" type="QString"/>
          </Option>
          <Option name="drawToAllParts" value="false" type="bool"/>
          <Option name="enabled" value="0" type="QString"/>
          <Option name="labelAnchorPoint" value="point_on_exterior" type="QString"/>
          <Option name="lineSymbol" value="&lt;symbol name=&quot;symbol&quot; alpha=&quot;1&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot; type=&quot;line&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; value=&quot;&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; value=&quot;collection&quot; type=&quot;QString&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer class=&quot;SimpleLine&quot; locked=&quot;0&quot; enabled=&quot;1&quot; pass=&quot;0&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;align_dash_pattern&quot; value=&quot;0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;capstyle&quot; value=&quot;square&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;customdash&quot; value=&quot;5;2&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;customdash_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;customdash_unit&quot; value=&quot;MM&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;dash_pattern_offset&quot; value=&quot;0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;dash_pattern_offset_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;dash_pattern_offset_unit&quot; value=&quot;MM&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;draw_inside_polygon&quot; value=&quot;0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;joinstyle&quot; value=&quot;bevel&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;line_color&quot; value=&quot;60,60,60,255&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;line_style&quot; value=&quot;solid&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;line_width&quot; value=&quot;0.3&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;line_width_unit&quot; value=&quot;MM&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;offset&quot; value=&quot;0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;offset_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;offset_unit&quot; value=&quot;MM&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;ring_filter&quot; value=&quot;0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;trim_distance_end&quot; value=&quot;0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;trim_distance_end_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;trim_distance_end_unit&quot; value=&quot;MM&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;trim_distance_start&quot; value=&quot;0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;trim_distance_start_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;trim_distance_start_unit&quot; value=&quot;MM&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;tweak_dash_pattern_on_corners&quot; value=&quot;0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;use_custom_dash&quot; value=&quot;0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;width_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot;/>&lt;/Option>&lt;prop k=&quot;align_dash_pattern&quot; v=&quot;0&quot;/>&lt;prop k=&quot;capstyle&quot; v=&quot;square&quot;/>&lt;prop k=&quot;customdash&quot; v=&quot;5;2&quot;/>&lt;prop k=&quot;customdash_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;customdash_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;dash_pattern_offset&quot; v=&quot;0&quot;/>&lt;prop k=&quot;dash_pattern_offset_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;dash_pattern_offset_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;draw_inside_polygon&quot; v=&quot;0&quot;/>&lt;prop k=&quot;joinstyle&quot; v=&quot;bevel&quot;/>&lt;prop k=&quot;line_color&quot; v=&quot;60,60,60,255&quot;/>&lt;prop k=&quot;line_style&quot; v=&quot;solid&quot;/>&lt;prop k=&quot;line_width&quot; v=&quot;0.3&quot;/>&lt;prop k=&quot;line_width_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;offset&quot; v=&quot;0&quot;/>&lt;prop k=&quot;offset_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;offset_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;ring_filter&quot; v=&quot;0&quot;/>&lt;prop k=&quot;trim_distance_end&quot; v=&quot;0&quot;/>&lt;prop k=&quot;trim_distance_end_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;trim_distance_end_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;trim_distance_start&quot; v=&quot;0&quot;/>&lt;prop k=&quot;trim_distance_start_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;trim_distance_start_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;tweak_dash_pattern_on_corners&quot; v=&quot;0&quot;/>&lt;prop k=&quot;use_custom_dash&quot; v=&quot;0&quot;/>&lt;prop k=&quot;width_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; value=&quot;&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; value=&quot;collection&quot; type=&quot;QString&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" type="QString"/>
          <Option name="minLength" value="0" type="double"/>
          <Option name="minLengthMapUnitScale" value="3x:0,0,0,0,0,0" type="QString"/>
          <Option name="minLengthUnit" value="MM" type="QString"/>
          <Option name="offsetFromAnchor" value="0" type="double"/>
          <Option name="offsetFromAnchorMapUnitScale" value="3x:0,0,0,0,0,0" type="QString"/>
          <Option name="offsetFromAnchorUnit" value="MM" type="QString"/>
          <Option name="offsetFromLabel" value="0" type="double"/>
          <Option name="offsetFromLabelMapUnitScale" value="3x:0,0,0,0,0,0" type="QString"/>
          <Option name="offsetFromLabelUnit" value="MM" type="QString"/>
        </Option>
      </callout>
    </settings>
  </labeling>
  <customproperties>
    <Option type="Map">
      <Option name="embeddedWidgets/count" value="0" type="int"/>
      <Option name="variableNames"/>
      <Option name="variableValues"/>
    </Option>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
    <DiagramCategory spacingUnit="MM" showAxis="1" penWidth="0" height="15" spacing="5" enabled="0" width="15" sizeType="MM" backgroundAlpha="255" penColor="#000000" direction="0" lineSizeType="MM" diagramOrientation="Up" scaleBasedVisibility="0" maxScaleDenominator="1e+08" labelPlacementMethod="XHeight" minScaleDenominator="0" spacingUnitScale="3x:0,0,0,0,0,0" lineSizeScale="3x:0,0,0,0,0,0" rotationOffset="270" opacity="1" scaleDependency="Area" penAlpha="255" backgroundColor="#ffffff" minimumSize="0" sizeScale="3x:0,0,0,0,0,0" barWidth="5">
      <fontProperties description="MS Shell Dlg 2,7.8,-1,5,50,0,0,0,0,0" style=""/>
      <attribute field="" label="" color="#000000"/>
      <axisSymbol>
        <symbol name="" alpha="1" force_rhr="0" clip_to_extent="1" type="line">
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" value="" type="QString"/>
              <Option name="properties"/>
              <Option name="type" value="collection" type="QString"/>
            </Option>
          </data_defined_properties>
          <layer class="SimpleLine" locked="0" enabled="1" pass="0">
            <Option type="Map">
              <Option name="align_dash_pattern" value="0" type="QString"/>
              <Option name="capstyle" value="square" type="QString"/>
              <Option name="customdash" value="5;2" type="QString"/>
              <Option name="customdash_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
              <Option name="customdash_unit" value="MM" type="QString"/>
              <Option name="dash_pattern_offset" value="0" type="QString"/>
              <Option name="dash_pattern_offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
              <Option name="dash_pattern_offset_unit" value="MM" type="QString"/>
              <Option name="draw_inside_polygon" value="0" type="QString"/>
              <Option name="joinstyle" value="bevel" type="QString"/>
              <Option name="line_color" value="35,35,35,255" type="QString"/>
              <Option name="line_style" value="solid" type="QString"/>
              <Option name="line_width" value="0.26" type="QString"/>
              <Option name="line_width_unit" value="MM" type="QString"/>
              <Option name="offset" value="0" type="QString"/>
              <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
              <Option name="offset_unit" value="MM" type="QString"/>
              <Option name="ring_filter" value="0" type="QString"/>
              <Option name="trim_distance_end" value="0" type="QString"/>
              <Option name="trim_distance_end_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
              <Option name="trim_distance_end_unit" value="MM" type="QString"/>
              <Option name="trim_distance_start" value="0" type="QString"/>
              <Option name="trim_distance_start_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
              <Option name="trim_distance_start_unit" value="MM" type="QString"/>
              <Option name="tweak_dash_pattern_on_corners" value="0" type="QString"/>
              <Option name="use_custom_dash" value="0" type="QString"/>
              <Option name="width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
            </Option>
            <prop k="align_dash_pattern" v="0"/>
            <prop k="capstyle" v="square"/>
            <prop k="customdash" v="5;2"/>
            <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="customdash_unit" v="MM"/>
            <prop k="dash_pattern_offset" v="0"/>
            <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="dash_pattern_offset_unit" v="MM"/>
            <prop k="draw_inside_polygon" v="0"/>
            <prop k="joinstyle" v="bevel"/>
            <prop k="line_color" v="35,35,35,255"/>
            <prop k="line_style" v="solid"/>
            <prop k="line_width" v="0.26"/>
            <prop k="line_width_unit" v="MM"/>
            <prop k="offset" v="0"/>
            <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="offset_unit" v="MM"/>
            <prop k="ring_filter" v="0"/>
            <prop k="trim_distance_end" v="0"/>
            <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="trim_distance_end_unit" v="MM"/>
            <prop k="trim_distance_start" v="0"/>
            <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="trim_distance_start_unit" v="MM"/>
            <prop k="tweak_dash_pattern_on_corners" v="0"/>
            <prop k="use_custom_dash" v="0"/>
            <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" value="" type="QString"/>
                <Option name="properties"/>
                <Option name="type" value="collection" type="QString"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings obstacle="0" linePlacementFlags="18" priority="0" showAll="1" dist="0" zIndex="0" placement="1">
    <properties>
      <Option type="Map">
        <Option name="name" value="" type="QString"/>
        <Option name="properties"/>
        <Option name="type" value="collection" type="QString"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration type="Map">
      <Option name="QgsGeometryGapCheck" type="Map">
        <Option name="allowedGapsBuffer" value="0" type="double"/>
        <Option name="allowedGapsEnabled" value="false" type="bool"/>
        <Option name="allowedGapsLayer" value="" type="QString"/>
      </Option>
    </checkConfiguration>
  </geometryOptions>
  <legend showLabelLegend="0" type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration/>
  <aliases/>
  <defaults/>
  <constraints/>
  <constraintExpressions/>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortExpression="" actionWidgetStyle="dropDown" sortOrder="0">
    <columns>
      <column hidden="1" type="actions" width="-1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- código: utf-8 -*-
"""
Formas QGIS podem ter uma função Python que é chamada quando o formulário é
aberto.

Use esta função para adicionar lógica extra para seus formulários.

Digite o nome da função na "função Python Init"
campo.
Um exemplo a seguir:
"""
de qgis.PyQt.QtWidgets importar QWidget

def my_form_open(diálogo, camada, feição):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable/>
  <labelOnTop/>
  <reuseLastValue/>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression></previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
