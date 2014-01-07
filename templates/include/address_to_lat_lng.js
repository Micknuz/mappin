    function addressToLatlng(address, callback){
        var geocoder = new google.maps.Geocoder();
        var result = Array();
        geocoder.geocode( { 'address': address, 'region': 'ko' }, function(results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                result['lat'] = results[0].geometry.location.lat();
                result['lng'] = results[0].geometry.location.lng();
            } else {
                result = "Unable to find address: " + status;
            }
            callback(result);
        });
    }
