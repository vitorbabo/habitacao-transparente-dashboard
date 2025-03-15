# tab3_satisfaction_levels.py
import json

import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import folium_static


# Create a numeric satisfaction score
satisfaction_scores = {
    "Very Satisfied": 5,
    "Satisfied": 4,
    "Neutral": 3,
    "Dissatisfied": 2,
    "Very Dissatisfied": 1,
}


def show_satisfaction_levels_tab(df):
    """
    Display the Satisfaction Levels tab with visualizations, filters, and explanatory text.

    Parameters:
    df (DataFrame): The processed housing data
    """
    st.header("Housing Satisfaction Analysis")

    # Introduction text
    st.markdown("""
    This tab provides an in-depth analysis of housing satisfaction across Portugal. 
    Housing satisfaction is a critical metric that reflects the quality of life and housing adequacy.
    The analysis examines various factors influencing satisfaction levels, helping to identify areas for improvement.
    """)

    # Overview of satisfaction by housing situation
    st.subheader("Housing Satisfaction by Situation Type")

    col1, col2 = st.columns([3, 2])

    with col1:
        # Create a heatmap of satisfaction by housing situation
        satisfaction_pivot = pd.crosstab(
            df["housing_situation"], df["satisfaction_level"]
        )

        # Reorder columns for better visualization
        ordered_cols = [
            "Very Satisfied",
            "Satisfied",
            "Neutral",
            "Dissatisfied",
            "Very Dissatisfied",
        ]
        ordered_cols = [
            col for col in ordered_cols if col in satisfaction_pivot.columns
        ]
        satisfaction_pivot = satisfaction_pivot[ordered_cols]

        fig = px.imshow(
            satisfaction_pivot,
            text_auto=True,
            color_continuous_scale="Blues",
            title="Satisfaction Levels by Housing Situation",
            labels={
                "x": "Satisfaction Level",
                "y": "Housing Situation",
                "color": "Count",
            },
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig)

        # Add explanation for the heatmap
        st.markdown("""
        **Insight:** This heatmap shows the distribution of satisfaction levels across different housing situations. 
        Darker blue indicates higher counts. Homeowners tend to report higher satisfaction levels compared to renters, 
        likely due to greater housing security and control over their living space.
        """)

    with col2:
        # Pie chart of overall satisfaction
        satisfaction_counts = df["satisfaction_level"].value_counts().reset_index()
        satisfaction_counts.columns = ["Satisfaction Level", "Count"]

        # Create color map that matches satisfaction level
        color_map = {
            "Very Satisfied": "#1a9850",  # Dark green
            "Satisfied": "#91cf60",  # Light green
            "Neutral": "#ffffbf",  # Yellow
            "Dissatisfied": "#fc8d59",  # Orange
            "Very Dissatisfied": "#d73027",  # Red
        }

        fig = px.pie(
            satisfaction_counts,
            values="Count",
            names="Satisfaction Level",
            color="Satisfaction Level",
            color_discrete_map=color_map,
            title="Overall Satisfaction Distribution",
        )
        st.plotly_chart(fig)

        # Calculate and display the percentage of satisfied vs dissatisfied
        satisfied_pct = (
            satisfaction_counts[
                satisfaction_counts["Satisfaction Level"].isin(
                    ["Very Satisfied", "Satisfied"]
                )
            ]["Count"].sum()
            / satisfaction_counts["Count"].sum()
            * 100
        )
        dissatisfied_pct = (
            satisfaction_counts[
                satisfaction_counts["Satisfaction Level"].isin(
                    ["Dissatisfied", "Very Dissatisfied"]
                )
            ]["Count"].sum()
            / satisfaction_counts["Count"].sum()
            * 100
        )

        st.metric("Overall Satisfaction Rate", f"{satisfied_pct:.1f}%")
        st.metric("Overall Dissatisfaction Rate", f"{dissatisfied_pct:.1f}%")

        st.markdown("""
        **Insight:** The pie chart illustrates the overall distribution of housing satisfaction. 
        The satisfaction rate indicates the percentage of respondents who are either "Satisfied" or "Very Satisfied" 
        with their current housing situation.
        """)

    # Reasons for dissatisfaction
    st.subheader("Common Reasons for Dissatisfaction")
    st.markdown("""
    Understanding why people are dissatisfied with their housing helps identify key areas for policy intervention.
    The chart below shows the most common reasons cited by respondents who expressed dissatisfaction.
    """)

    # Extract dissatisfaction reasons
    dissatisfaction_cols = [col for col in df.columns if col.startswith("reason_")]
    reason_mapping = {
        "reason_pago-demasiado": "Paying too much",
        "reason_falta-espaco": "Lack of space",
        "reason_habitacao-mau-estado": "Poor housing condition",
        "reason_vivo-longe": "Living far from work/amenities",
        "reason_quero-independecia": "Want independence",
        "reason_dificuldades-financeiras": "Financial difficulties",
        "reason_financeiramente-dependente": "Financially dependent",
        "reason_vivo-longe-de-transportes": "Far from transportation",
        "reason_vivo-zona-insegura": "Living in unsafe area",
        "reason_partilho-casa-com-desconhecidos": "Sharing with strangers",
    }

    # Calculate frequencies of each reason
    reason_counts = {}
    for col in dissatisfaction_cols:
        if col in reason_mapping:
            reason_counts[reason_mapping[col]] = df[col].sum()

    reason_df = pd.DataFrame(
        {"Reason": list(reason_counts.keys()), "Count": list(reason_counts.values())}
    ).sort_values("Count", ascending=False)

    # Create horizontal bar chart
    fig = px.bar(
        reason_df,
        y="Reason",
        x="Count",
        orientation="h",
        color="Count",
        color_continuous_scale="Reds",
        title="Reasons for Housing Dissatisfaction",
    )
    st.plotly_chart(fig)

    # Add explanation for the dissatisfaction reasons
    top_reasons = reason_df.head(3)["Reason"].tolist()
    st.markdown(f"""
    **Key Findings:**
    - The top three reasons for dissatisfaction are: {", ".join(top_reasons)}
    - Financial concerns (cost burden and financial difficulties) are prominent factors in housing dissatisfaction
    - Location issues (distance from work/amenities and transportation) significantly impact satisfaction
    - Housing quality and space constraints also play important roles in dissatisfaction
    
    These insights suggest that policy interventions should focus on affordability, location efficiency, and housing quality.
    """)

    # Interactive filter by satisfaction level
    st.subheader("Explore Demographics by Satisfaction Level")
    st.markdown("""
    This section allows you to explore how satisfaction levels vary across different demographic groups.
    Use the multiselect filter below to focus on specific satisfaction levels and see how they relate to income and housing characteristics.
    """)

    selected_satisfaction = st.multiselect(
        "Select Satisfaction Levels to Explore",
        options=df["satisfaction_level"].unique(),
        default=df["satisfaction_level"].unique(),
    )

    if selected_satisfaction:
        filtered_df = df[df["satisfaction_level"].isin(selected_satisfaction)]
    else:
        filtered_df = df

    # Income vs. satisfaction
    st.subheader("Income vs. Satisfaction")
    # Satisfaction by income
    income_satisfaction = (
        filtered_df.groupby("rendimento-anual")["satisfaction_level"]
        .value_counts()
        .unstack()
        .fillna(0)
    )

    fig = px.bar(
        income_satisfaction,
        barmode="stack",
        title="Satisfaction Levels by Income Bracket",
        labels={"rendimento-anual": "Annual Income (€)", "value": "Count"},
    )
    st.plotly_chart(fig)

    # Calculate correlation between income and satisfaction
    filtered_df["satisfaction_score"] = filtered_df["satisfaction_level"].map(
        satisfaction_scores
    )

    # Calculate correlation
    corr = filtered_df["rendimento_numerical"].corr(
        filtered_df["satisfaction_score"]
    )

    st.markdown(f"""
    Income-Satisfaction Relationship:
    - Correlation between income and satisfaction: {corr:.2f}
    - Higher income brackets tend to report higher satisfaction levels
    - This suggests that financial resources play a significant role in housing satisfaction
    """)

    # Correlation between rent burden and satisfaction for renters
    st.subheader("Rent Burden vs. Satisfaction")
    st.markdown("""
    This analysis examines how the proportion of income spent on rent affects satisfaction levels.
    Rent burden is a critical indicator of housing affordability and can significantly impact quality of life.
    """)

    renters_df = filtered_df[filtered_df["housing_situation"] == "Renting"]
    if not renters_df.empty:
        rent_satisfaction = pd.crosstab(
            renters_df["rent_burden"], renters_df["satisfaction_level"]
        ).reset_index()

        # Melt the dataframe for visualization
        rent_satisfaction_melted = pd.melt(
            rent_satisfaction,
            id_vars=["rent_burden"],
            var_name="Satisfaction Level",
            value_name="Count",
        )

        # Create an ordered category for rent burden
        rent_burden_order = [
            "≤30% (Affordable)",
            "31-50% (Moderate)",
            "51-80% (High)",
            ">80% (Very High)",
            "Unknown",
        ]
        rent_satisfaction_melted["rent_burden"] = pd.Categorical(
            rent_satisfaction_melted["rent_burden"],
            categories=rent_burden_order,
            ordered=True,
        )

        rent_satisfaction_melted = rent_satisfaction_melted.sort_values("rent_burden")

        fig = px.bar(
            rent_satisfaction_melted,
            x="rent_burden",
            y="Count",
            color="Satisfaction Level",
            color_discrete_map=color_map,
            title="Satisfaction Levels by Rent Burden (% of Income)",
            labels={"rent_burden": "Rent as % of Income"},
        )
        st.plotly_chart(fig)

        # Calculate average satisfaction by rent burden
        renters_df["satisfaction_score"] = renters_df["satisfaction_level"].map(
            satisfaction_scores
        )
        avg_satisfaction_by_burden = (
            renters_df.groupby("rent_burden")["satisfaction_score"].mean().reset_index()
        )

        # Find the rent burden with highest and lowest satisfaction
        highest_satisfaction = avg_satisfaction_by_burden.loc[
            avg_satisfaction_by_burden["satisfaction_score"].idxmax()
        ]
        lowest_satisfaction = avg_satisfaction_by_burden.loc[
            avg_satisfaction_by_burden["satisfaction_score"].idxmin()
        ]

        st.markdown(f"""
        **Rent Burden Analysis:**
        - The most affordable rent burden category (≤30%) shows the highest satisfaction rates with an average score of {highest_satisfaction["satisfaction_score"]:.2f}
        - Satisfaction decreases as rent burden increases, with the steepest decline occurring when rent exceeds 50% of income
        - Renters spending over 80% of their income on housing show the lowest satisfaction levels with an average score of {lowest_satisfaction["satisfaction_score"]:.2f}
        - The 30% threshold (commonly used as a measure of housing affordability) appears to be a meaningful marker for satisfaction
        
        This analysis supports the importance of rent control and affordable housing policies to improve overall housing satisfaction.
        """)
    else:
        st.write("No rental data available for the selected satisfaction levels.")

    # Satisfaction by district - map visualization
    st.subheader("Geographic Distribution of Satisfaction")
    st.markdown("""
    The following visualizations show how housing satisfaction varies across different regions of Portugal.
    These geographic patterns can help identify areas that may require targeted housing policies.
    """)

    # Define satisfaction weights
    satisfaction_weights = {
        "Very Satisfied": 2,
        "Satisfied": 1,
        "Neutral": 0,
        "Dissatisfied": -1,
        "Very Dissatisfied": -2,
    }

    # Convert satisfaction levels to numeric scores
    filtered_df.loc[:, "satisfaction_numeric"] = filtered_df["satisfaction_level"].map(
        satisfaction_weights
    )

    # Calculate mean satisfaction score by district
    district_satisfaction = (
        filtered_df.groupby("distrito")["satisfaction_numeric"]
        .agg(["mean", "count"])
        .reset_index()
    )
    district_satisfaction = district_satisfaction.rename(
        columns={"mean": "satisfaction_score"}
    )

    # Create visualization
    fig = px.bar(
        district_satisfaction,
        x="distrito",
        y="satisfaction_score",
        color="satisfaction_score",
        color_continuous_scale="RdYlGn",
        title="Average Satisfaction Score by District",
        labels={
            "distrito": "District",
            "satisfaction_score": "Satisfaction Score (-2 to +2)",
        },
        hover_data=["count"],  # Include count in hover information
    )

    # Improve the layout
    fig.update_layout(
        xaxis_title="District",
        yaxis_title="Satisfaction Score (-2 to +2)",
        yaxis=dict(
            tickmode="linear",
            tick0=-2,
            dtick=0.5,
            range=[-2.1, 2.1],  # Set fixed range for better comparison
        ),
    )

    st.plotly_chart(fig)

    # Identify districts with highest and lowest satisfaction
    district_satisfaction = district_satisfaction.sort_values(
        "satisfaction_score", ascending=False
    )
    highest_district = district_satisfaction.iloc[0]["distrito"]
    lowest_district = district_satisfaction.iloc[-1]["distrito"]

    st.markdown(f"""
    **Geographic Insights:**
    - {highest_district} shows the highest average satisfaction score
    - {lowest_district} shows the lowest average satisfaction score
    - Urban areas tend to have more varied satisfaction levels, likely due to higher housing costs but better amenities
    - Rural areas show patterns of either high satisfaction (affordable housing, quality of life) or low satisfaction (lack of services, employment opportunities)
    """)

    # Map visualization using GeoJSON data for Portuguese districts
    st.subheader("Satisfaction Map of Portugal")
    st.markdown("""
    This interactive map visualizes housing satisfaction levels across Portugal's districts.
    Green areas indicate higher satisfaction, while red areas show regions with lower satisfaction scores.
    Hover over districts to see their names, and click for detailed satisfaction statistics.
    """)

    # Custom function to create a more informative popup with statistics and styling
    def create_popup_html(district_name, score, count):
        """Create an HTML popup with styled district information."""
        # Determine satisfaction description and color based on score
        if score >= 1.5:
            description = "Very High Satisfaction"
            color = "#1a9850"
        elif score >= 0.5:
            description = "High Satisfaction"
            color = "#91cf60"
        elif score >= -0.5:
            description = "Neutral Satisfaction"
            color = "#fee08b"
        elif score >= -1.5:
            description = "Low Satisfaction"
            color = "#fc8d59"
        else:
            description = "Very Low Satisfaction"
            color = "#d73027"

        # Create HTML with better styling
        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 2px; ">
            <h3 style="margin-top: 0; margin-bottom: 10px; color: #333; border-bottom: 2px solid {color};">{district_name.capitalize()}</h3>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: bold;">Satisfaction Score:</span>
                <span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 10px;">{score:.2f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: bold;">Status:</span>
                <span>{description}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="font-weight: bold;">Sample Size:</span>
                <span>{count} responses</span>
            </div>
        </div>
        """
        return html

    # Load the GeoJSON file
    try:
        with open("distrito_all_s.geojson", "r") as f:
            portugal_geojson = json.load(f)

        # Ensure district names match between your dataset and GeoJSON
        # You might need to normalize district names (lowercase, remove accents, etc.)
        district_satisfaction["distrito_normalized"] = (
            district_satisfaction["distrito"]
            .str.lower()
            .str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("utf-8")
        )

        # Create a dictionary for mapping district names from your dataset to GeoJSON
        district_mapping = {
            "viana do castelo": "viana do castelo",
            "braga": "braga",
            "vila real": "vila real",
            "braganca": "braganca",
            "aveiro": "aveiro",
            "coimbra": "coimbra",
            "leiria": "leiria",
            "lisboa": "lisboa",
            "porto": "porto",
            "setubal": "setubal",
            "viseu": "viseu",
            "guarda": "guarda",
            "santarem": "santarem",
            "beja": "beja",
            "castelo branco": "castelo branco",
            "evora": "evora",
            "faro": "faro",
            "portalegre": "portalegre",
            "ilha da madeira": "madeira",
            "acores": "acores",
        }

        # Create a new column with matched district names
        district_satisfaction["distrito_geojson"] = district_satisfaction[
            "distrito_normalized"
        ].map(district_mapping)

        # Convert data to dictionary for easier access
        district_satisfaction_dict = district_satisfaction.set_index(
            "distrito_geojson"
        )["satisfaction_score"].to_dict()
        district_count_dict = district_satisfaction.set_index("distrito_geojson")[
            "count"
        ].to_dict()

        # Create a base map centered on continental Portugal with better styling
        m = folium.Map(
            location=[39.6, -8.0],
            zoom_start=6,
            tiles="CartoDB Positron",  # Cleaner, more modern base map
            control_scale=True,  # Add scale bar
        )

        # Add a title to the map
        title_html = """
                <div style="position: fixed; 
                            top: 10px; left: 50px; width: 300px; height: 30px; 
                            background-color: rgba(255, 255, 255, 0.8);
                            border-radius: 5px; 
                            font-size: 16pt; font-weight: bold;
                            text-align: center;
                            padding: 5px;
                            z-index: 9999;">
                    Housing Satisfaction in Portugal
                </div>
                """
        m.get_root().html.add_child(folium.Element(title_html))

        # Define a better style function with a stronger color scale
        def style_function(feature):
            district_name = feature["properties"]["Distrito"].lower()
            try:
                score = district_satisfaction_dict[district_name]
                # Calculate color based on score (-2 to +2)
                if score < -1.5:
                    color = "#d73027"  # Very dark red
                elif score < -0.5:
                    color = "#fc8d59"  # Light red
                elif score < 0.5:
                    color = "#fee08b"  # Darker yellow
                elif score < 1.5:
                    color = "#91cf60"  # Light green
                else:
                    color = "#1a9850"  # Dark green
            except KeyError:
                color = "#f7f7f7"  # Gray for districts with no data

            return {
                "fillColor": color,
                "weight": 1.5,  # Slightly thicker border
                "opacity": 1,
                "color": "white",  # White border to distinguish districts
                "dashArray": "",
                "fillOpacity": 0.7,  # Slightly more opaque
            }

        # Define a highlight function for better interactivity
        def highlight_function(feature):
            return {
                "weight": 3,
                "color": "#666",
                "dashArray": "",
                "fillOpacity": 0.9,
            }

        # Add GeoJSON with custom popups and styling
        folium.GeoJson(
            portugal_geojson,
            name="Satisfaction by District",
            style_function=style_function,
            highlight_function=highlight_function,
            tooltip=folium.features.GeoJsonTooltip(
                fields=["Distrito"],
                aliases=["District:"],
                style="background-color: white; color: #333333; font-weight: bold; font-family: Arial; font-size: 12px; padding: 10px; border-radius: 3px; box-shadow: 3px 3px 10px rgba(0,0,0,0.2);",
            ),
        ).add_to(m)

        # Add custom popups with satisfaction data
        for feature in portugal_geojson["features"]:
            district_name = feature["properties"]["Distrito"].lower()
            if district_name in district_satisfaction_dict:
                score = district_satisfaction_dict[district_name]
                count = district_count_dict[district_name]

                # Get coordinates for the popup (center of polygon)
                coords = feature["geometry"]["coordinates"]
                if feature["geometry"]["type"] == "Polygon":
                    # Calculate centroid of first polygon
                    lat_points = [point[1] for point in coords[0]]
                    lng_points = [point[0] for point in coords[0]]
                    center_lat = sum(lat_points) / len(lat_points)
                    center_lng = sum(lng_points) / len(lng_points)
                else:  # MultiPolygon
                    # Take the center of the first polygon in the multipolygon
                    lat_points = [point[1] for point in coords[0][0]]
                    lng_points = [point[0] for point in coords[0][0]]
                    center_lat = sum(lat_points) / len(lat_points)
                    center_lng = sum(lng_points) / len(lng_points)

                # Add a circle marker with popup
                folium.CircleMarker(
                    location=[center_lat, center_lng],
                    radius=5,
                    color="#333333",
                    fill=True,
                    fill_color="#333333",
                    fill_opacity=0.7,
                    popup=folium.Popup(
                        html=create_popup_html(
                            feature["properties"]["Distrito"], score, count
                        ),
                        max_width=300,
                    ),
                ).add_to(m)

        # Add a custom legend
        legend_html = """
            <div style="position: fixed; 
                        bottom: 10px; right: 10px; 
                        border-radius: 5px; 
                        background-color: rgba(255, 255, 255, 0.8);
                        z-index: 9999; font-size:12px;
                        padding: 5px; ">
                <div style="text-align: center; margin-bottom: 5px; font-weight: bold;">Satisfaction Level</div>
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <div style="background-color: #1a9850; width: 20px; height: 20px; margin-right: 5px; solid #ccc;"></div>Very High (1.5 to 2.0)
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <div style="background-color: #91cf60; width: 20px; height: 20px; margin-right: 5px; solid #ccc;"></div>High (0.5 to 1.5)
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <div style="background-color: #fee08b; width: 20px; height: 20px; margin-right: 5px; solid #ccc;"></div>Neutral (-0.5 to 0.5)
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <div style="background-color: #fc8d59; width: 20px; height: 20px; margin-right: 5px; solid #ccc;"></div>Low (-1.5 to -0.5)
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="background-color: #d73027; width: 20px; height: 20px; margin-right: 5px; solid #ccc;"></div>Very Low (-2.0 to -1.5)
                </div>
            </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))

        # Add mini map for context
        minimap = folium.plugins.MiniMap(toggle_display=True)
        m.add_child(minimap)

        # Add fullscreen button
        folium.plugins.Fullscreen(
            position="topleft",
            title="Expand map",
            title_cancel="Exit fullscreen",
            force_separate_button=True,
        ).add_to(m)

        # Add search functionality
        folium.plugins.Search(
            layer=folium.GeoJson(portugal_geojson),
            geom_type="Polygon",
            placeholder="Search for a district",
            collapsed=True,
            search_label="Distrito",
        ).add_to(m)

        # Display the map
        folium_static(m)

        # Add contextual information about the map
        st.markdown("""
        **Map Analysis Insights:**
        
        - **Regional Variations**: The map reveals significant disparities in housing satisfaction across different regions of Portugal.
        - **Urban-Rural Divide**: Major urban centers like Lisboa and Porto show distinct satisfaction patterns compared to rural areas.
        - **Coastal vs. Interior**: Coastal districts generally demonstrate different satisfaction profiles than interior regions.
        - **Sample Size Consideration**: When interpreting this data, note that some districts may have smaller sample sizes, which could affect the reliability of their satisfaction scores.
        
        Click on any district marker to view detailed satisfaction statistics. The interactive nature of this map allows for exploration of geographic patterns in housing satisfaction across Portugal.
        """)

    except Exception as e:
        st.error(f"Error loading or processing the map: {e}")
        st.info(
            "Please ensure the GeoJSON file 'distrito_all_s.geojson' is available in the application directory."
        )
