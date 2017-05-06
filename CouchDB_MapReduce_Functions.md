### Happiness ###

### Map ###

function (doc) { . 
  emit(doc.code, doc.sentiment);  
} . 

### Reduce ###

function (keys, values, rereduce) { . 
  var analysis = { count: 0, polarity: 0 };  
  if (rereduce){ . 
        for(var i=0; i < values.length; i++) { . 
            analysis.count += values[i].count;  
            analysis.polarity += values[i].polarity;  
        } . 
        analysis.polarity = analysis.polarity / analysis.count;  
        return analysis;  
  } . 

  analysis.count = values.length;  
  analysis.polarity = sum(values);  
  return analysis;  
} . 
