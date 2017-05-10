// Properties within geojson file, and feature within maps api.
const properties = {
  id: 'SA2_Code_2011',
  bounds: 'bounds',
  name: 'SA2_Name_2011',
  income: 'Average_taxable_income',
  overweight: 'ovrwght_p_me_2_rate_3_11_7_13',
  obese: 'obese_p_me_2_rate_3_11_7_13',
  smoker: 'smokers_me_2_rate_3_11_7_13'
};

const JSON_FILE = 'data/sa2_dump.json';

// Used to store range of aurin data sets.
var data_ranges = {
    income: {
        max: 0,
        min: Number.MAX_SAFE_INTEGER
    },
    smoker: {
        max: 0,
        min: 100
    },
    overweight: {
        max: 0,
        min: 100
    },
    obese: {
        max: 0,
        min: 100
    },
    overweightAndObese: {
        max: 0,
        min: 100
    },
    tweetCount: {
        max: 0,
        min: Number.MAX_SAFE_INTEGER
    },
    tweetPolarity: {
        max: -1,
        min: 1
    }
}

// Current dataset to display.
var display = []

// Store data from db.
var tweet_lookup = {}

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
    map.data.loadGeoJson(JSON_FILE);

    // Load tweets, storing data in a global object.
    loadTweets();

    // Store extra info for bounds, mins and maxs.
    google.maps.event.addListener(map.data, 'addfeature', function (e) {
        // Caluclate bounds.
        var bounds = new google.maps.LatLngBounds();
        e.feature.getGeometry().forEachLatLng(function(path) {
            bounds.extend(path);
        });
        e.feature.setProperty(properties.bounds, bounds);

        // Update ranges for aurin values.
        for (var key in data_ranges) {
            if (key == "overweightAndObese") {
                value = e.feature.getProperty(properties.overweight) + e.feature.getProperty(properties.obese);
                if (value == 0) {
                    continue;
                }
            } else {
                value = e.feature.getProperty(properties[key]);
            }
            if (value > data_ranges[key].max) {
                data_ranges[key].max = value;
            }
            if (value < data_ranges[key].min && value != null) {
                data_ranges[key].min = value;
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

/* http://stackoverflow.com/questions/2499567/how-to-make-a-json-call-to-a-url/2499647#2499647 */
function get(yourUrl){
    var Httpreq = new XMLHttpRequest(); // a new request
    Httpreq.open("GET",yourUrl,false);
    Httpreq.send(null);
    return Httpreq.responseText;
}

// Loads the tweets from provided DB, stores in global lookup object.
function loadTweets() {
    tweet_obj = JSON.parse(get('http://localhost:15984/processed_tweets/_design/sentiment_analysis/_view/sentiment_analysis?reduce=true&group=true'));
    for (var i = 0; i < tweet_obj.rows.length; i++) {
        data = tweet_obj.rows[i]
        tweet_lookup[data.key] = data.value;
        count = data.value.count;
        if (count < data_ranges.tweetCount.min) {
            data_ranges.tweetCount.min = count
        }
        if (count > data_ranges.tweetCount.max) {
            data_ranges.tweetCount.max = count
        }
        polarity = data.value.polarity;
        if (polarity < data_ranges.tweetPolarity.min) {
            data_ranges.tweetPolarity.min = polarity
        }
        if (polarity > data_ranges.tweetPolarity.max) {
            data_ranges.tweetPolarity.max = polarity
        }
    }
}

/* Set style of map based on selected variable. */
function generateMapStyle(f) {
    var strokeColor = "gray"
    var strokeWeight = 1
    var fillOpacity = 0.5


    // Do not overaly.
    if (display.length == 0) {
        fillOpacity = 0;
    // Overalay a single feature.
    } else if (display.length == 1) {
        disp = display[0]
        if (disp) {
            norm = getNormalisedValue(f, disp);
            if (norm < 0 || norm > 100) {
                fillOpacity = 0;
            }
            var fillColor = numberToColorHsl(norm);
        } else {
            fillOpacity = 0;
        }
    // Correlate two features.
    } else if (display.length == 2) {
        disp1 = display[0]
        disp2 = display[1]

        norm1 = getNormalisedValue(f, disp1);
        norm2 = getNormalisedValue(f, disp2);

        if (norm1 < 0 || norm2 > 100 || norm2 < 0 || norm2 > 100) {
            fillOpacity = 0;
        }

        var fillColor = numberToColorHsl(correlate(norm1, norm2));
    }

    return {
        strokeColor: strokeColor,
        strokeWeight: strokeWeight,
        fillOpacity: fillOpacity,
        fillColor: fillColor
    }
}

function getNormalisedValue(f, disp) {
    code = f.getProperty(properties.id)
    value = null
    if (disp == "overweightAndObese") {
        overweight = f.getProperty(properties.overweight);
        obese = f.getProperty(properties.obese);
        value = 0;
        if (overweight != null && obese != null) {
            value = overweight + obese;
        }
    } else {
        if (disp == "tweetCount") {
            value = tweet_lookup[code] ? tweet_lookup[code].count : null
        } else if (disp == "tweetPolarity") {
            value = tweet_lookup[code] ? tweet_lookup[code].polarity : null
        } else {
            value = f.getProperty(properties[disp]);
        }
        if (value == null) {
            value = Number.MIN_SAFE_INTEGER
        }
    }
    // Normalise and get color representation.
    norm = normalise(value, data_ranges[disp].max, data_ranges[disp].min);

    // Flip all but income.
    if (disp != "income" && disp != "tweetCount" && disp != "tweetPolarity") {
        norm = 1 - norm;
    }

    return norm * 100;
}

/* Generate content for info window -- Data for each SA2 (feature) */
function generateInfoWindowContent(f) {
    // Format values for display.
    income = f.getProperty(properties.income)
    if (income) {
        income = "$" + income.toFixed(0);
    }
    smokers = f.getProperty(properties.smoker).toFixed(2)
    overweight = f.getProperty(properties.overweight).toFixed(2)
    obese = f.getProperty(properties.obese).toFixed(2)
    oo = null;
    if (obese != null && overweight != null) {
        oo = (parseFloat(obese) + parseFloat(overweight)).toFixed(2)
    }
    name = f.getProperty(properties.name)
    code = f.getProperty(properties.id)
    tweet_data = tweet_lookup[code]
    count = null
    polarity = null
    if (tweet_data) {
        count = tweet_data.count
        polarity = tweet_data.polarity.toFixed(2)
    }


    str = "<div>"
    str += "<h4>" + name + "</h4>"
    str += "<table>"
    str += "<tr><td> Avg. taxable income: </td><td>" + income + "</td></tr>"
    str += "<tr><td> Smokers per 100 people: </td><td>" + smokers + "</td></tr>"
    str += "<tr><td> Overweight per 100 people: </td><td>" + overweight + "</td></tr>"
    str += "<tr><td> Obese per 100 people: </td><td>" + obese + "</td></tr>"
    str += "<tr><td> Combined overweight and obese: </td><td>" + oo + "</td></tr>"
    str += "<tr><td> Tweets: </td><td>" + count + "</td></tr>"
    str += "<tr><td> Tweet Polarity </td><td>" + polarity + "</td></tr>"
    str += "</table>"
    return str
}

function correlate(n1, n2) {
    return 100 - Math.abs(n1-n2);
}

function refreshData(new_display) {
    display = new_display;
    map.data.setStyle(generateMapStyle);
}

function refreshDataNew() {
    var checkCount = 0
    disp = []

    if (document.checks.income.checked) {
        checkCount += 1
    }

    if (document.checks.smoker.checked) {
        checkCount += 1
    }

    if (document.checks.overweight.checked) {
        checkCount += 1
    }

    if (document.checks.obese.checked) {
        checkCount += 1
    }

    if (document.checks.overweightAndObese.checked) {
        checkCount += 1
    }

    if (document.checks.tweetCount.checked) {
        checkCount += 1
    }

    if (document.checks.tweetPolarity.checked) {
        checkCount += 1
    }

    if (checkCount == 3) {
        return false;
    }

    if (document.checks.income.checked) {
        checkCount += 1
        disp.push("income")
    }

    if (document.checks.smoker.checked) {
        checkCount += 1
        disp.push("smoker")
    }

    if (document.checks.overweight.checked) {
        checkCount += 1
        disp.push("overweight")
    }

    if (document.checks.obese.checked) {
        checkCount += 1
        disp.push("obese")
    }

    if (document.checks.overweightAndObese.checked) {
        checkCount += 1
        disp.push("overweightAndObese")
    }

    if (document.checks.tweetCount.checked) {
        checkCount += 1
        disp.push("tweetCount")
    }

    if (document.checks.tweetPolarity.checked) {
        checkCount += 1
        disp.push("tweetPolarity")
    }

    display = disp;

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