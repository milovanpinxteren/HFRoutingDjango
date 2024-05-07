"""
Map maker in Folium. Takes a dictionary/json input,
with key as label name, value as info and location points
e.g.: {'hubs': [{'name': '', 'address': '', 'lat': 51.708738, 'lon': 5.2674352}],
'customers': [{'name': '', 'address': '', 'lat': 51.9863478, 'lon': 5.8763971}],
 'operators': [{'name': '', 'address': '', 'lat': 51.4236127, 'lon': 5.4635217}]}
"""

import folium
from HFRoutingApp.data.color_data import ColorData
from branca.element import Template, MacroElement


class MapMaker:

    def make_map(self, data):
        map_obj = folium.Map(location=[51.69217, 5.2957742], zoom_start=7)
        legend_entries = ""

        for group in data:
            legend_entries += f'&nbsp; {group.capitalize()} &nbsp; <i class="fa fa-map-marker fa-sm" style="color:{ColorData.colors.get(group, "red")}"></i><br>'
            folium_group = folium.FeatureGroup(group).add_to(map_obj)
            for location in data[group]:
                info = f"Type: {group} <br/> Name: {location['name']}<br/>Address: {location['address']}"
                icon_color = ColorData.colors.get(group, "red")
                folium.Marker((location['lat'], location['lon']), icon=folium.Icon(icon_color),
                              popup=folium.Popup(info, max_width=200)).add_to(folium_group)

        folium.LayerControl().add_to(map_obj)
        height = 25 + (len(data) * 20)
        template = f""" 
        {{% macro html(this, kwargs) %}}
        <div style="
            position: fixed; 
            bottom: 13px;
            right: 0;
            width: 120px;
            height: {height}px; 
            border:1px solid grey;
            background: whitesmoke; 
            z-index:9999;">
            &nbsp; <b>Legenda</b> <br>
            {legend_entries}
            
          </div>
          {{% endmacro %}}
        """
        macro = MacroElement()
        macro._template = Template(template)

        map_obj.get_root().add_child(macro)

        return map_obj
