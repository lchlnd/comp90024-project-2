// Properties within geojson file, and feature within maps api.
const properties = {
  id: 'SA2_Code_2011',
  bounds: 'bounds',
  name: 'SA2_Name_2011',
  income: 'Average_taxable_income'
};

// Used to store range of aurin data sets.
var aurin_ranges = {
    income: {
        max: 0,
        min: 999999
    }
}

// Current dataset to display.
var display = null

/* Load map centred around Melbourne */
var map;
function initMap() {
    // Basic map settings.
    var melbourne = {lat: -37.8136, lng: 144.9631};
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 9,
        center: melbourne
    });

    // Info window to be displayed on hover.
    var infowindow = new google.maps.InfoWindow({
        content: 'NIL',
    });

    // Load map overlay.
    map.data.loadGeoJson('data/sa2.json');

    // Store extra info for bounds, mins and maxs.
    google.maps.event.addListener(map.data, 'addfeature', function (e) {
        // Caluclate bounds.
        var bounds = new google.maps.LatLngBounds();
        e.feature.getGeometry().forEachLatLng(function(path) {
            bounds.extend(path);
        });
        e.feature.setProperty(properties.bounds, bounds);

        // Update ranges for aurin values.
        for (var key in aurin_ranges) {
            value = e.feature.getProperty(properties[key]);
            if (value > aurin_ranges[key].max) {
                aurin_ranges[key].max = value;
            }
            if (value < aurin_ranges[key].min && value != null) {
                aurin_ranges[key].min = value;
            }
        }
    });

    // Define hover event to display SA2 information in window.
    map.data.addListener('mouseover', function (event) {
        // Remove previous and highlight current.
        map.data.revertStyle();
        map.data.overrideStyle(event.feature, { strokeWeight: 5 });

        // Setup infowindow if loaded SA2.
        if (event.feature) {
            infowindow.setContent(generateInfoWindowContent(event.feature));
            infowindow.setPosition(event.feature.getProperty(properties.bounds).getCenter());
            infowindow.setOptions({ pixelOffset: new google.maps.Size(0, -10) });
            infowindow.open(map);
        }
    });

    // Setup styles.
    map.data.setStyle(generateMapStyle);
}

/* Set style of map based on selected variable. */
function generateMapStyle(f) {
    var strokeColor = "gray"
    var strokeWeight = 1
    var fillOpacity = 0.5

    if (display) {
        value = f.getProperty(properties[display]);

        // Normalise and get color representation.
        norm = normalise(value, aurin_ranges[display].max, aurin_ranges[display].min);
        if (norm <= 0) {
            fillOpacity = 0;
        }
        norm *= 100;
        var fillColor = numberToColorHsl(norm);
    } else {
        fillOpacity = 0;
    }

    return {
        strokeColor: strokeColor,
        strokeWeight: strokeWeight,
        fillOpacity: fillOpacity,
        fillColor: fillColor
    }
}

/* Generate content for info window -- Data for each SA2 (feature) */
function generateInfoWindowContent(f) {
    // Format values for display.
    income = f.getProperty(properties.income)
    if (income) {
        income = "$" + income.toFixed(0)
    }
    name = f.getProperty(properties.name)

    str = "<div>"
    str += "<h4>" + name + "</h4>"
    str += "<table>"
    str += "<tr><td> Avg. taxable income: </td><td>" + income + "</td></tr>"
    str += "</table>"
    return str
}

function refreshData(new_display) {
    display = new_display;
    map.data.setStyle(generateMapStyle);
}

/**
 * http://stackoverflow.com/questions/2353211/hsl-to-rgb-color-conversion
 *
 * Converts an HSL color value to RGB. Conversion formula
 * adapted from http://en.wikipedia.org/wiki/HSL_color_space.
 * Assumes h, s, and l are contained in the set [0, 1] and
 * returns r, g, and b in the set [0, 255].
 *
 * @param   Number  h       The hue
 * @param   Number  s       The saturation
 * @param   Number  l       The lightness
 * @return  Array           The RGB representation
 */
function hslToRgb(h, s, l){
    var r, g, b;

    if(s == 0){
        r = g = b = l; // achromatic
    }else{
        function hue2rgb(p, q, t){
            if(t < 0) t += 1;
            if(t > 1) t -= 1;
            if(t < 1/6) return p + (q - p) * 6 * t;
            if(t < 1/2) return q;
            if(t < 2/3) return p + (q - p) * (2/3 - t) * 6;
            return p;
        }

        var q = l < 0.5 ? l * (1 + s) : l + s - l * s;
        var p = 2 * l - q;
        r = hue2rgb(p, q, h + 1/3);
        g = hue2rgb(p, q, h);
        b = hue2rgb(p, q, h - 1/3);
    }

    return [Math.floor(r * 255), Math.floor(g * 255), Math.floor(b * 255)];
}

// convert a number to a color using hsl
function numberToColorHsl(i) {
    // as the function expects a value between 0 and 1, and red = 0° and green = 120°
    // we convert the input to the appropriate hue value
    var hue = i * 1.2 / 360;
    // we convert hsl to rgb (saturation 100%, lightness 50%)
    var rgb = hslToRgb(hue, 1, .5);
    // we format to css value and return
    return 'rgb(' + rgb[0] + ',' + rgb[1] + ',' + rgb[2] + ')';
}

function normalise(val, max, min) { return (val - min) / (max - min); }


/* http://stackoverflow.com/questions/5623838/rgb-to-hex-and-hex-to-rgb */
function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}