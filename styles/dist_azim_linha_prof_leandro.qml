<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.40.10-Bratislava" styleCategories="Symbology|Labeling" labelsEnabled="1">
  <renderer-v2 enableorderby="0" forceraster="0" referencescale="-1" symbollevels="0" type="RuleRenderer">
    <rules key="{334b76f9-5f1d-454c-bd2e-650c985a327a}">
      <rule symbol="0" label="Cotagem" key="{dad1eba0-5e95-4bd6-93e6-774c221eea62}"/>
      <rule symbol="1" label="Linha" key="{7b53ef7e-332d-461f-a96b-8ef7ba300509}" checkstate="0"/>
    </rules>
    <symbols>
      <symbol alpha="1" frame_rate="10" name="0" clip_to_extent="1" is_animated="0" force_rhr="0" type="line">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" value="" type="QString"/>
            <Option name="properties"/>
            <Option name="type" value="collection" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer class="GeometryGenerator" pass="0" enabled="1" id="{9e8ee906-a25a-4978-835c-6a22381ab7e7}" locked="0">
          <Option type="Map">
            <Option name="SymbolType" value="Line" type="QString"/>
            <Option name="geometryModifier" value=" segments_to_lines( $geometry)" type="QString"/>
            <Option name="units" value="MapUnit" type="QString"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" value="" type="QString"/>
              <Option name="properties"/>
              <Option name="type" value="collection" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" name="@0@0" clip_to_extent="1" is_animated="0" force_rhr="0" type="line">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" value="" type="QString"/>
                <Option name="properties"/>
                <Option name="type" value="collection" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="ArrowLine" pass="0" enabled="1" id="{1ec99c85-27a4-4a14-b879-e061be252b20}" locked="0">
              <Option type="Map">
                <Option name="arrow_start_width" value="1" type="QString"/>
                <Option name="arrow_start_width_unit" value="MM" type="QString"/>
                <Option name="arrow_start_width_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="arrow_type" value="0" type="QString"/>
                <Option name="arrow_width" value="0.2" type="QString"/>
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
                <Option name="offset" value="-4" type="QString"/>
                <Option name="offset_unit" value="MM" type="QString"/>
                <Option name="offset_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="ring_filter" value="0" type="QString"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" value="" type="QString"/>
                  <Option name="properties" type="Map">
                    <Option name="offset" type="Map">
                      <Option name="active" value="false" type="bool"/>
                      <Option name="type" value="1" type="int"/>
                      <Option name="val" value="" type="QString"/>
                    </Option>
                  </Option>
                  <Option name="type" value="collection" type="QString"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" name="@@0@0@0" clip_to_extent="1" is_animated="0" force_rhr="0" type="fill">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" value="" type="QString"/>
                    <Option name="properties"/>
                    <Option name="type" value="collection" type="QString"/>
                  </Option>
                </data_defined_properties>
                <layer class="SimpleFill" pass="0" enabled="1" id="{c086ad3c-c850-4ea8-b8d3-629bef07c0d3}" locked="0">
                  <Option type="Map">
                    <Option name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="color" value="0,0,0,255,rgb:0,0,0,1" type="QString"/>
                    <Option name="joinstyle" value="bevel" type="QString"/>
                    <Option name="offset" value="0,0" type="QString"/>
                    <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="offset_unit" value="MM" type="QString"/>
                    <Option name="outline_color" value="0,0,0,255,rgb:0,0,0,1" type="QString"/>
                    <Option name="outline_style" value="no" type="QString"/>
                    <Option name="outline_width" value="0.1" type="QString"/>
                    <Option name="outline_width_unit" value="MM" type="QString"/>
                    <Option name="style" value="solid" type="QString"/>
                  </Option>
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
            <layer class="MarkerLine" pass="0" enabled="1" id="{23a13281-dfae-4d15-bd22-d1da52666952}" locked="0">
              <Option type="Map">
                <Option name="average_angle_length" value="4" type="QString"/>
                <Option name="average_angle_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="average_angle_unit" value="MM" type="QString"/>
                <Option name="interval" value="3" type="QString"/>
                <Option name="interval_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="interval_unit" value="RenderMetersInMapUnits" type="QString"/>
                <Option name="offset" value="0" type="QString"/>
                <Option name="offset_along_line" value="0" type="QString"/>
                <Option name="offset_along_line_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_along_line_unit" value="RenderMetersInMapUnits" type="QString"/>
                <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_unit" value="RenderMetersInMapUnits" type="QString"/>
                <Option name="place_on_every_part" value="true" type="bool"/>
                <Option name="placements" value="LastVertex|FirstVertex|InnerVertices" type="QString"/>
                <Option name="ring_filter" value="0" type="QString"/>
                <Option name="rotate" value="1" type="QString"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" value="" type="QString"/>
                  <Option name="properties"/>
                  <Option name="type" value="collection" type="QString"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" name="@@0@0@1" clip_to_extent="1" is_animated="0" force_rhr="0" type="marker">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" value="" type="QString"/>
                    <Option name="properties"/>
                    <Option name="type" value="collection" type="QString"/>
                  </Option>
                </data_defined_properties>
                <layer class="SimpleMarker" pass="0" enabled="1" id="{502d509e-4f10-413e-9713-2e83f69bb928}" locked="0">
                  <Option type="Map">
                    <Option name="angle" value="0" type="QString"/>
                    <Option name="cap_style" value="square" type="QString"/>
                    <Option name="color" value="255,0,0,255,rgb:1,0,0,1" type="QString"/>
                    <Option name="horizontal_anchor_point" value="1" type="QString"/>
                    <Option name="joinstyle" value="bevel" type="QString"/>
                    <Option name="name" value="line" type="QString"/>
                    <Option name="offset" value="-0.00000000000000006,0" type="QString"/>
                    <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="offset_unit" value="MM" type="QString"/>
                    <Option name="outline_color" value="0,0,0,255,rgb:0,0,0,1" type="QString"/>
                    <Option name="outline_style" value="solid" type="QString"/>
                    <Option name="outline_width" value="0" type="QString"/>
                    <Option name="outline_width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="outline_width_unit" value="MM" type="QString"/>
                    <Option name="scale_method" value="diameter" type="QString"/>
                    <Option name="size" value="8" type="QString"/>
                    <Option name="size_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="size_unit" value="MM" type="QString"/>
                    <Option name="vertical_anchor_point" value="2" type="QString"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" value="" type="QString"/>
                      <Option name="properties" type="Map">
                        <Option name="size" type="Map">
                          <Option name="active" value="false" type="bool"/>
                          <Option name="expression" value="if (&quot;Offset&quot; >0,&quot;Offset&quot; +2,0)" type="QString"/>
                          <Option name="type" value="3" type="int"/>
                        </Option>
                      </Option>
                      <Option name="type" value="collection" type="QString"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" name="1" clip_to_extent="1" is_animated="0" force_rhr="0" type="line">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" value="" type="QString"/>
            <Option name="properties"/>
            <Option name="type" value="collection" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleLine" pass="0" enabled="1" id="{042cd6b2-e7a0-4047-9fa6-e15778cfd612}" locked="0">
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
            <Option name="line_color" value="225,89,137,255,rgb:0.88235294117647056,0.34901960784313724,0.53725490196078429,1" type="QString"/>
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
    <data-defined-properties>
      <Option type="Map">
        <Option name="name" value="" type="QString"/>
        <Option name="properties"/>
        <Option name="type" value="collection" type="QString"/>
      </Option>
    </data-defined-properties>
    <effect enabled="0" type="effectStack">
      <effect type="dropShadow">
        <Option type="Map">
          <Option name="blend_mode" value="13" type="QString"/>
          <Option name="blur_level" value="2.645" type="QString"/>
          <Option name="blur_unit" value="MM" type="QString"/>
          <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
          <Option name="color" value="0,0,0,255,rgb:0,0,0,1" type="QString"/>
          <Option name="draw_mode" value="2" type="QString"/>
          <Option name="enabled" value="0" type="QString"/>
          <Option name="offset_angle" value="135" type="QString"/>
          <Option name="offset_distance" value="2" type="QString"/>
          <Option name="offset_unit" value="MM" type="QString"/>
          <Option name="offset_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
          <Option name="opacity" value="1" type="QString"/>
        </Option>
      </effect>
      <effect type="outerGlow">
        <Option type="Map">
          <Option name="blend_mode" value="0" type="QString"/>
          <Option name="blur_level" value="0.7935" type="QString"/>
          <Option name="blur_unit" value="MM" type="QString"/>
          <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
          <Option name="color1" value="0,0,255,255,rgb:0,0,1,1" type="QString"/>
          <Option name="color2" value="0,255,0,255,rgb:0,1,0,1" type="QString"/>
          <Option name="color_type" value="0" type="QString"/>
          <Option name="direction" value="ccw" type="QString"/>
          <Option name="discrete" value="0" type="QString"/>
          <Option name="draw_mode" value="2" type="QString"/>
          <Option name="enabled" value="1" type="QString"/>
          <Option name="opacity" value="0.5" type="QString"/>
          <Option name="rampType" value="gradient" type="QString"/>
          <Option name="single_color" value="255,255,255,255,rgb:1,1,1,1" type="QString"/>
          <Option name="spec" value="rgb" type="QString"/>
          <Option name="spread" value="2" type="QString"/>
          <Option name="spread_unit" value="MM" type="QString"/>
          <Option name="spread_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
        </Option>
      </effect>
      <effect type="drawSource">
        <Option type="Map">
          <Option name="blend_mode" value="0" type="QString"/>
          <Option name="draw_mode" value="2" type="QString"/>
          <Option name="enabled" value="1" type="QString"/>
          <Option name="opacity" value="1" type="QString"/>
        </Option>
      </effect>
      <effect type="innerShadow">
        <Option type="Map">
          <Option name="blend_mode" value="13" type="QString"/>
          <Option name="blur_level" value="2.645" type="QString"/>
          <Option name="blur_unit" value="MM" type="QString"/>
          <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
          <Option name="color" value="0,0,0,255,rgb:0,0,0,1" type="QString"/>
          <Option name="draw_mode" value="2" type="QString"/>
          <Option name="enabled" value="0" type="QString"/>
          <Option name="offset_angle" value="135" type="QString"/>
          <Option name="offset_distance" value="2" type="QString"/>
          <Option name="offset_unit" value="MM" type="QString"/>
          <Option name="offset_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
          <Option name="opacity" value="1" type="QString"/>
        </Option>
      </effect>
      <effect type="innerGlow">
        <Option type="Map">
          <Option name="blend_mode" value="0" type="QString"/>
          <Option name="blur_level" value="0.7935" type="QString"/>
          <Option name="blur_unit" value="MM" type="QString"/>
          <Option name="blur_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
          <Option name="color1" value="0,0,255,255,rgb:0,0,1,1" type="QString"/>
          <Option name="color2" value="0,255,0,255,rgb:0,1,0,1" type="QString"/>
          <Option name="color_type" value="0" type="QString"/>
          <Option name="direction" value="ccw" type="QString"/>
          <Option name="discrete" value="0" type="QString"/>
          <Option name="draw_mode" value="2" type="QString"/>
          <Option name="enabled" value="0" type="QString"/>
          <Option name="opacity" value="0.5" type="QString"/>
          <Option name="rampType" value="gradient" type="QString"/>
          <Option name="single_color" value="255,255,255,255,rgb:1,1,1,1" type="QString"/>
          <Option name="spec" value="rgb" type="QString"/>
          <Option name="spread" value="2" type="QString"/>
          <Option name="spread_unit" value="MM" type="QString"/>
          <Option name="spread_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
        </Option>
      </effect>
    </effect>
  </renderer-v2>
  <selection mode="Default">
    <selectionColor invalid="1"/>
    <selectionSymbol>
      <symbol alpha="1" frame_rate="10" name="" clip_to_extent="1" is_animated="0" force_rhr="0" type="line">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" value="" type="QString"/>
            <Option name="properties"/>
            <Option name="type" value="collection" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleLine" pass="0" enabled="1" id="{83b5609f-6be0-4b3d-9b84-4b987f17837e}" locked="0">
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
            <Option name="line_color" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString"/>
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
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" value="" type="QString"/>
              <Option name="properties"/>
              <Option name="type" value="collection" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </selectionSymbol>
  </selection>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style fontWordSpacing="0" isExpression="1" namedStyle="Bold" multilineHeight="1" textOpacity="1" fontSizeUnit="Point" tabStopDistanceUnit="Point" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontItalic="0" forcedItalic="0" fontUnderline="0" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" legendString="Aa" fontFamily="Arial" forcedBold="0" fontKerning="1" textColor="50,50,50,255,rgb:0.19607843137254902,0.19607843137254902,0.19607843137254902,1" allowHtml="0" textOrientation="horizontal" tabStopDistance="80" stretchFactor="100" fontStrikeout="0" fontWeight="75" fieldName="format_number([EXPRESSION],2)  || ' m' ||  '\n'  || &#xd;&#xa;dd2dms( &#xd;&#xa; degrees( azimuth( start_point( $geometry) ,  end_point( $geometry)) ),&#xd;&#xa; 1)" multilineHeightUnit="Percentage" tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" blendMode="0" fontSize="9" fontLetterSpacing="0" capitalization="0" useSubstitutions="0">
        <families/>
        <text-buffer bufferSize="1" bufferSizeUnits="MM" bufferBlendMode="0" bufferNoFill="1" bufferOpacity="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="250,250,250,255,rgb:0.98039215686274506,0.98039215686274506,0.98039215686274506,1" bufferDraw="0" bufferJoinStyle="128"/>
        <text-mask maskType="0" maskSize="3" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskJoinStyle="128" maskedSymbolLayers="Dimensioning_c8c6cc4a_e5cc_45ad_8226_50af6c977dc2;{c086ad3c-c850-4ea8-b8d3-629bef07c0d3};dimensioning_86b7f8a8_6890_4f7b_b0e7_5c136084d547;{c086ad3c-c850-4ea8-b8d3-629bef07c0d3};teste1_b964c126_cd16_4951_aeb1_7b3e375afa52;{502d509e-4f10-413e-9713-2e83f69bb928};teste1_b964c126_cd16_4951_aeb1_7b3e375afa52;{c086ad3c-c850-4ea8-b8d3-629bef07c0d3};teste1_b964c126_cd16_4951_aeb1_7b3e375afa52;{042cd6b2-e7a0-4047-9fa6-e15778cfd612}" maskSize2="3" maskSizeUnits="MM" maskEnabled="1" maskOpacity="1"/>
        <background shapeJoinStyle="64" shapeRotation="0" shapeOpacity="1" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeDraw="0" shapeBorderWidthUnit="Point" shapeRadiiX="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeRotationType="0" shapeRadiiUnit="Point" shapeSizeType="0" shapeOffsetUnit="Point" shapeBorderWidth="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeBorderColor="128,128,128,255,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,1" shapeBlendMode="0" shapeRadiiY="0" shapeType="0" shapeSVGFile="" shapeSizeUnit="Point" shapeSizeY="0" shapeFillColor="255,255,255,255,rgb:1,1,1,1" shapeOffsetY="0" shapeOffsetX="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0">
          <symbol alpha="1" frame_rate="10" name="markerSymbol" clip_to_extent="1" is_animated="0" force_rhr="0" type="marker">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" value="" type="QString"/>
                <Option name="properties"/>
                <Option name="type" value="collection" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleMarker" pass="0" enabled="1" id="" locked="0">
              <Option type="Map">
                <Option name="angle" value="0" type="QString"/>
                <Option name="cap_style" value="square" type="QString"/>
                <Option name="color" value="255,158,23,255,rgb:1,0.61960784313725492,0.09019607843137255,1" type="QString"/>
                <Option name="horizontal_anchor_point" value="1" type="QString"/>
                <Option name="joinstyle" value="bevel" type="QString"/>
                <Option name="name" value="circle" type="QString"/>
                <Option name="offset" value="0,0" type="QString"/>
                <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_unit" value="MM" type="QString"/>
                <Option name="outline_color" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString"/>
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
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" value="" type="QString"/>
                  <Option name="properties"/>
                  <Option name="type" value="collection" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
          <symbol alpha="1" frame_rate="10" name="fillSymbol" clip_to_extent="1" is_animated="0" force_rhr="0" type="fill">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" value="" type="QString"/>
                <Option name="properties"/>
                <Option name="type" value="collection" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleFill" pass="0" enabled="1" id="" locked="0">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="color" value="255,255,255,255,rgb:1,1,1,1" type="QString"/>
                <Option name="joinstyle" value="bevel" type="QString"/>
                <Option name="offset" value="0,0" type="QString"/>
                <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_unit" value="MM" type="QString"/>
                <Option name="outline_color" value="128,128,128,255,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,1" type="QString"/>
                <Option name="outline_style" value="no" type="QString"/>
                <Option name="outline_width" value="0" type="QString"/>
                <Option name="outline_width_unit" value="Point" type="QString"/>
                <Option name="style" value="solid" type="QString"/>
              </Option>
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
        <shadow shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowRadiusUnit="MM" shadowScale="100" shadowRadiusAlphaOnly="0" shadowOffsetDist="1" shadowOffsetUnit="MM" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOpacity="0.69999999999999996" shadowOffsetGlobal="1" shadowRadius="1.5" shadowBlendMode="6" shadowDraw="0" shadowUnder="0" shadowColor="0,0,0,255,rgb:0,0,0,1"/>
        <dd_properties>
          <Option type="Map">
            <Option name="name" value="" type="QString"/>
            <Option name="properties"/>
            <Option name="type" value="collection" type="QString"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format autoWrapLength="0" multilineAlign="1" placeDirectionSymbol="0" plussign="0" formatNumbers="0" leftDirectionSymbol="&lt;" useMaxLineLengthForAutoWrap="1" decimals="3" rightDirectionSymbol=">" reverseDirectionSymbol="0" wrapChar="" addDirectionSymbol="0"/>
      <placement allowDegraded="0" preserveRotation="1" lineAnchorClipping="0" maxCurvedCharAngleOut="-25" dist="0" fitInPolygonOnly="0" lineAnchorTextPoint="FollowPlacement" maximumDistance="0" placement="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" lineAnchorPercent="0.5" geometryGeneratorType="PointGeometry" offsetType="0" maximumDistanceUnit="MM" repeatDistanceUnits="Point" geometryGeneratorEnabled="0" quadOffset="4" layerType="LineGeometry" overrunDistanceUnit="MM" centroidInside="0" yOffset="0" distUnits="MM" lineAnchorType="0" maxCurvedCharAngleIn="25" rotationAngle="0" priority="5" repeatDistance="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" xOffset="0" geometryGenerator="" distMapUnitScale="3x:0,0,0,0,0,0" centroidWhole="0" placementFlags="2" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" overlapHandling="PreventOverlap" prioritization="PreferCloser" polygonPlacementFlags="2" maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" offsetUnits="MM" overrunDistance="0" rotationUnit="AngleDegrees"/>
      <rendering obstacle="1" maxNumLabels="2000" scaleVisibility="0" zIndex="0" minFeatureSize="0" drawLabels="1" scaleMin="0" obstacleType="1" unplacedVisibility="0" mergeLines="0" fontMaxPixelSize="10000" obstacleFactor="1" scaleMax="0" limitNumLabels="0" upsidedownLabels="0" labelPerPart="0" fontMinPixelSize="3" fontLimitPixelSize="0"/>
      <dd_properties>
        <Option type="Map">
          <Option name="name" value="" type="QString"/>
          <Option name="properties" type="Map">
            <Option name="LabelDistance" type="Map">
              <Option name="active" value="false" type="bool"/>
              <Option name="type" value="1" type="int"/>
              <Option name="val" value="" type="QString"/>
            </Option>
            <Option name="LinePlacementFlags" type="Map">
              <Option name="active" value="false" type="bool"/>
              <Option name="type" value="1" type="int"/>
              <Option name="val" value="" type="QString"/>
            </Option>
          </Option>
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
          <Option name="lineSymbol" value="&lt;symbol alpha=&quot;1&quot; frame_rate=&quot;10&quot; name=&quot;symbol&quot; clip_to_extent=&quot;1&quot; is_animated=&quot;0&quot; force_rhr=&quot;0&quot; type=&quot;line&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; value=&quot;&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; value=&quot;collection&quot; type=&quot;QString&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer class=&quot;SimpleLine&quot; pass=&quot;0&quot; enabled=&quot;1&quot; id=&quot;{c1e03bf8-d528-45d5-9df7-8d84db8e813f}&quot; locked=&quot;0&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;align_dash_pattern&quot; value=&quot;0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;capstyle&quot; value=&quot;square&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;customdash&quot; value=&quot;5;2&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;customdash_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;customdash_unit&quot; value=&quot;MM&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;dash_pattern_offset&quot; value=&quot;0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;dash_pattern_offset_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;dash_pattern_offset_unit&quot; value=&quot;MM&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;draw_inside_polygon&quot; value=&quot;0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;joinstyle&quot; value=&quot;bevel&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;line_color&quot; value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;line_style&quot; value=&quot;solid&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;line_width&quot; value=&quot;0.3&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;line_width_unit&quot; value=&quot;MM&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;offset&quot; value=&quot;0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;offset_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;offset_unit&quot; value=&quot;MM&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;ring_filter&quot; value=&quot;0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;trim_distance_end&quot; value=&quot;0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;trim_distance_end_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;trim_distance_end_unit&quot; value=&quot;MM&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;trim_distance_start&quot; value=&quot;0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;trim_distance_start_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;trim_distance_start_unit&quot; value=&quot;MM&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;tweak_dash_pattern_on_corners&quot; value=&quot;0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;use_custom_dash&quot; value=&quot;0&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;width_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; value=&quot;&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; value=&quot;collection&quot; type=&quot;QString&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" type="QString"/>
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
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerGeometryType>1</layerGeometryType>
</qgis>
