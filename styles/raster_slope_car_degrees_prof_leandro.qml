<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Symbology" version="3.44.8-Solothurn">
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option name="CAR-Slope-Degrees" type="QString" value="Prof_Leandro_Franca"/>
      <Option name="properties"/>
      <Option name="type" type="QString" value="collection"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling zoomedOutResamplingMethod="nearestNeighbour" maxOversampling="2" enabled="false" zoomedInResamplingMethod="nearestNeighbour"/>
    </provider>
    <rasterrenderer nodataColor="" alphaBand="-1" band="1" opacity="1" type="singlebandpseudocolor" classificationMax="90" classificationMin="0">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <rastershader>
        <colorrampshader minimumValue="0" labelPrecision="2" clip="0" maximumValue="90" colorRampType="DISCRETE" classificationMode="2">
          <colorramp name="[source]" type="gradient">
            <Option type="Map">
              <Option name="color1" type="QString" value="26,152,80,255"/>
              <Option name="color2" type="QString" value="215,48,39,255"/>
              <Option name="discrete" type="QString" value="0"/>
              <Option name="rampType" type="QString" value="gradient"/>
              <Option name="spec" type="QString" value="rgb"/>
              <Option name="stops" type="QString" value="0.5;254,224,139,255;rgb;ccw"/>
            </Option>
          </colorramp>
          <item label="0° – 25° (Baixa a moderada declividade)" color="#1a9850" alpha="255" value="25"/>
          <item label="25° – 45° (Alta declividade / atenção ambiental)" color="#fee08b" alpha="255" value="45"/>
          <item label="> 45° (APP - Encosta com declividade superior a 45°)" color="#d73027" alpha="255" value="inf"/>
          <rampLegendSettings minimumLabel="" prefix="" suffix="" direction="0" maximumLabel="" orientation="2" useContinuousLegend="0">
            <numericFormat id="basic">
              <Option type="Map">
                <Option name="decimal_separator" type="invalid"/>
                <Option name="decimals" type="int" value="2"/>
                <Option name="rounding_type" type="int" value="0"/>
                <Option name="show_plus" type="bool" value="false"/>
                <Option name="show_thousand_separator" type="bool" value="true"/>
                <Option name="show_trailing_zeros" type="bool" value="false"/>
                <Option name="thousand_separator" type="invalid"/>
              </Option>
            </numericFormat>
          </rampLegendSettings>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness="0" gamma="1" contrast="0"/>
    <huesaturation colorizeStrength="100" invertColors="0" colorizeBlue="128" colorizeRed="255" colorizeGreen="128" colorizeOn="0" grayscaleMode="0" saturation="0"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
