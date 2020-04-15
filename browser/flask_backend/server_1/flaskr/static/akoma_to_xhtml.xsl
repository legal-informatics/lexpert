<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:akn="http://docs.oasis-open.org/legaldocml/ns/akn/3.0">

    <xsl:template match="/akn:akomaNtoso">
        <html>
            <head>
                <link rel="stylesheet" type="text/css" href="akoma_ntoso.css" />
                <title>
                    <xsl:value-of select="akn:act/@name"/>
                </title>
            </head>
            <body>
                <h2 id="naslov">
                    <xsl:value-of select="akn:act/@name"/>
                </h2>
                <xsl:apply-templates select="akn:act/akn:body/akn:chapter"/>
            </body>
        </html>
    </xsl:template>

    <!-- templejt za glavu -->
    <xsl:template match="akn:chapter">
        <div class="glava" id="{@wId}">
            <p>
                <xsl:value-of select="akn:num"/> &#160;
                <xsl:value-of select="akn:heading"/>
            </p>
            <xsl:apply-templates select="akn:section"/>
            <xsl:apply-templates select="akn:article"/>
        </div>
    </xsl:template>

    <!-- templejt za odeljak -->
    <xsl:template match="akn:section">
        <div class="odeljak" id="{@wId}">
            <p>
                <xsl:value-of select="akn:num"/>
                <xsl:value-of select="akn:heading"/>
            </p>
        </div>
        <xsl:apply-templates select="akn:article"/>
    </xsl:template>

    <!-- templejt za clan -->
    <xsl:template match="akn:article">
        <div class="clan" id="{@wId}">
            <p>
                <xsl:value-of select="akn:num"/> &#160;
                <xsl:value-of select="akn:heading"/>
            </p>
            <xsl:apply-templates select="akn:paragraph"/>
        </div>
    </xsl:template>

    <!-- templejt za stav -->
    <xsl:template match="akn:paragraph">
        <div class="stav" id="{@wId}">
            <p>
                <xsl:apply-templates select="akn:intro"/>
                <xsl:apply-templates select="akn:content/akn:p"/>
            </p>
            <xsl:apply-templates select="akn:point"/>
        </div>
    </xsl:template>

    <!-- templejt za tacku -->
    <xsl:template match="akn:point">
        <div class="tacka" id="{@wId}">
            <p>
                <xsl:value-of select="akn:num"/>
                <xsl:apply-templates select="akn:content/akn:p"/>
            </p>
        </div>
        <xsl:apply-templates select="akn:content/akn:point"/>
    </xsl:template>

    <!-- templejt za alineju -->
    <xsl:template match="akn:alinea">
        <p class="alineja" id="{@wId}">
            <xsl:apply-templates select="akn:content/akn:p"/>
        </p>
    </xsl:template>

    <!-- templejt za tagovanje linkova unutar P contenta -->
    <xsl:template match="akn:p//*">
        <xsl:copy>
            <xsl:copy-of select="@*" />
            <xsl:apply-templates />
        </xsl:copy>
    </xsl:template>

    <xsl:template match="akn:p//akn:ref">
        <a href="#{@href}">
            <xsl:apply-templates />
        </a>
    </xsl:template>
    <!-- templejt za tagovanje linkova unutar P contenta -->

</xsl:stylesheet>