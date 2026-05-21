<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Symbology" version="3.44.8-Solothurn">
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option name="FAO" type="QString" value="Prof_Leandro_Franca"/>
      <Option name="properties"/>
      <Option name="type" type="QString" value="collection"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling zoomedOutResamplingMethod="nearestNeighbour" maxOversampling="2" enabled="false" zoomedInResamplingMethod="nearestNeighbour"/>
    </provider>
    <rasterrenderer nodataColor="" alphaBand="-1" band="1" opacity="1" type="singlebandpseudocolor" classificationMax="60" classificationMin="0">
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
        <colorrampshader minimumValue="0" labelPrecision="4" clip="0" maximumValue="60" colorRampType="DISCRETE" classificationMode="2">
          <colorramp name="[source]" type="gradient">
            <Option type="Map">
              <Option name="color1" type="QString" value="130,164,255,255,hsv:0.621,0.48969253070878155,1,1"/>
              <Option name="color2" type="QString" value="127,0,0,255,rgb:0.4980392,0,0,1"/>
              <Option name="direction" type="QString" value="ccw"/>
              <Option name="discrete" type="QString" value="0"/>
              <Option name="rampType" type="QString" value="gradient"/>
              <Option name="spec" type="QString" value="rgb"/>
              <Option name="stops" type="QString" value="0.00333333;130,164,255,255,hsv:0.621,0.48969253070878155,1,1;rgb;ccw:0.00833333;102,189,99,255,rgb:0.4,0.7411765,0.3882353,1;rgb;ccw:0.0166667;166,217,106,255,rgb:0.6509804,0.8509804,0.4156863,1;rgb;ccw:0.0333333;217,239,139,255,rgb:0.8509804,0.9372549,0.545098,1;rgb;ccw:0.0833333;255,255,191,255,rgb:1,1,0.7490196,1;rgb;ccw:0.166667;254,224,139,255,rgb:0.9960784,0.8784314,0.545098,1;rgb;ccw:0.25;253,174,97,255,rgb:0.9921569,0.6823529,0.3803922,1;rgb;ccw:0.5;244,109,67,255,rgb:0.9568627,0.427451,0.2627451,1;rgb;ccw:1;215,48,39,255,rgb:0.8431373,0.1882353,0.1529412,1;rgb;ccw"/>
            </Option>
          </colorramp>
          <item label="0% – 0.2% (Flat)" color="#82a4ff" alpha="255" value="0.2"/>
          <item label="0.2% – 0.5% (Level)" color="#66bd63" alpha="255" value="0.5"/>
          <item label="0.5% – 1.0% (Nearly level)" color="#a6d96a" alpha="255" value="1"/>
          <item label="1.0% – 2.0% (Very gently sloping)" color="#d9ef8b" alpha="255" value="2"/>
          <item label="2% – 5% (Gently sloping)" color="#ffffbf" alpha="255" value="5"/>
          <item label="5% – 10% (Sloping)" color="#fee08b" alpha="255" value="10"/>
          <item label="10% – 15% (Strongly sloping)" color="#fdae61" alpha="255" value="15"/>
          <item label="15% – 30% (Moderately steep)" color="#f46d43" alpha="255" value="30"/>
          <item label="30% – 60% (Steep)" color="#d73027" alpha="255" value="60"/>
          <item label="> 60% (Very steep)" color="#7f0000" alpha="255" value="inf"/>
          <rampLegendSettings minimumLabel="" prefix="" suffix="" direction="0" maximumLabel="" orientation="2" useContinuousLegend="1">
            <numericFormat id="basic">
              <Option type="Map">
                <Option name="decimal_separator" type="invalid"/>
                <Option name="decimals" type="int" value="6"/>
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
