<xsl:stylesheet 
 version='1.0'
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

 <xsl:import href="lib.xsl"/>

 <!-- select "text" as output method -->
 <xsl:output method="text" omit-xml-declaration="yes"/>

 <!-- suppress output of random text -->
 <xsl:template match="text()"/>
 
 <xsl:template match="/">

  <xsl:for-each select="output/locus">
   <xsl:variable name="kmax">
    <xsl:call-template name="max-value">
     <xsl:with-param name="path" select="population/allelecounts/distinctalleles"/>
    </xsl:call-template>
   </xsl:variable>
   
   <xsl:variable name="all-allele-names"
    select="population/allelecounts[distinctalleles=$kmax]/allele/@name"/>

   <xsl:variable name="locus-name" select="substring-after(@name, '*')"/>
   
   <xsl:for-each select="population[allelecounts[@role!='no-data']]">

    <xsl:call-template name="R-by-allele">
     <xsl:with-param name="kmax" select="$kmax"/>
     <xsl:with-param name="locus-name" select="$locus-name"/>
     <xsl:with-param name="pop-name"
     select="substring-before(filename, '.pop')"/>
     <xsl:with-param name="allele-list" select="allelecounts/allele"/>
     <xsl:with-param name="all-allele-names" select="$all-allele-names"/>
    </xsl:call-template>

    <xsl:call-template name="R-by-count">
     <xsl:with-param name="kmax" select="$kmax"/>
     <xsl:with-param name="locus-name" select="$locus-name"/>
     <xsl:with-param name="pop-name"
      select="substring-before(filename, '.pop')"/>
     <xsl:with-param name="allele-list" select="allelecounts/allele"/>
    </xsl:call-template>

   </xsl:for-each>  
  </xsl:for-each>
  
 </xsl:template>

 <xsl:template name="R-init-vectors">
  <xsl:param name="kmax"/>
  <!-- initialize a vector with appropriate number of bins -->
  <xsl:text>allele.counts = rep(c(0),</xsl:text><xsl:value-of
   select="$kmax"/><xsl:text>)
</xsl:text>
  <xsl:text>allele.freq = rep(c(0),</xsl:text><xsl:value-of
   select="$kmax"/><xsl:text>)
</xsl:text>
  <xsl:text>allele.names = rep(c("*"),</xsl:text><xsl:value-of
   select="$kmax"/><xsl:text>)
</xsl:text>

 </xsl:template>

 <xsl:template name="R-by-allele">
  <xsl:param name="kmax"/>
  <xsl:param name="pop-name"/>
  <xsl:param name="allele-list"/>
  <xsl:param name="all-allele-names"/>

  <xsl:call-template name="R-init-vectors">
   <xsl:with-param name="kmax" select="$kmax"/>
  </xsl:call-template>

  <xsl:for-each select="$all-allele-names">
   <xsl:sort select="@name" data-type="text" order="ascending"/>
   <xsl:variable name="thename" select="."/>
   <xsl:text>allele.freq[</xsl:text><xsl:value-of select="position()"/>
   <xsl:text>] = </xsl:text>
   <xsl:choose>
    <xsl:when test="$allele-list[@name=$thename]">
     <xsl:value-of select="$allele-list[@name=$thename]/frequency"/>
    </xsl:when>
    <xsl:otherwise><xsl:text>0</xsl:text>
    </xsl:otherwise>
   </xsl:choose>
<xsl:text>
</xsl:text>   
<xsl:text>allele.names[</xsl:text><xsl:value-of select="position()"/>
   <xsl:text>] = "</xsl:text>
   <xsl:value-of select="$thename"/>
   <xsl:text>"
</xsl:text>
  </xsl:for-each>
<xsl:text>names(allele.freq) = allele.names
postscript("</xsl:text><xsl:value-of select="$locus-name"/><xsl:text>-</xsl:text><xsl:value-of select="$pop-name"/><xsl:text>-by-allele.ps")
barplot(allele.freq,las=2)
title("Allele frequencies ordered by allele for locus </xsl:text><xsl:value-of
select="$locus-name"/><xsl:text> in population </xsl:text><xsl:value-of select="$pop-name"/><xsl:text>")
rm(allele.counts)
rm(allele.names)


</xsl:text>

 </xsl:template>

 <xsl:template name="R-by-count">
  <xsl:param name="kmax"/>
  <xsl:param name="locus-name"/>
  <xsl:param name="pop-name"/>
  <xsl:param name="allele-list"/>

  <xsl:call-template name="R-init-vectors">
   <xsl:with-param name="kmax" select="$kmax"/>
  </xsl:call-template>

  <!-- loop through alleles and assign each vector with count and
  label -->

  <xsl:for-each select="$allele-list">

   <xsl:sort select="count" data-type="number" order="descending"/>
   <xsl:text>allele.counts[</xsl:text><xsl:value-of select="position()"/>
   <xsl:text>] = </xsl:text>
   <xsl:value-of select="count"/>
   <xsl:text>
</xsl:text>
<xsl:text>allele.freq[</xsl:text><xsl:value-of select="position()"/>
   <xsl:text>] = </xsl:text>
   <xsl:value-of select="frequency"/>
   <xsl:text>
</xsl:text>
   <xsl:text>allele.names[</xsl:text><xsl:value-of select="position()"/>
   <xsl:text>] = "</xsl:text>
   <xsl:value-of select="@name"/>
   <xsl:text>"
</xsl:text>
  </xsl:for-each>
<xsl:text>allele.counts
names(allele.counts) = allele.names
names(allele.freq) = allele.names
postscript("</xsl:text><xsl:value-of select="$locus-name"/><xsl:text>-</xsl:text><xsl:value-of select="$pop-name"/><xsl:text>.ps")
barplot(allele.freq,las=2)
title("Allele frequencies for locus </xsl:text><xsl:value-of
select="$locus-name"/><xsl:text> in population </xsl:text><xsl:value-of select="$pop-name"/><xsl:text>")
rm(allele.counts)
rm(allele.names)

</xsl:text>
 </xsl:template>

</xsl:stylesheet>

<!-- 
Local variables:
mode: xml
sgml-default-dtd-file: "xsl.ced"
sgml-indent-step: 1
sgml-indent-data: 1
End:
-->
