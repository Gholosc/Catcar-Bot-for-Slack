import json
import requests
import unittest

WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?q={0}&units=metric' 
# Format with a string of form 'Christchurch, NZ'

def _extractUseful(weather_data):
    info = {'desc_main': str(weather_data[u'weather'][0][u'main']),
            'desc_second': str(weather_data[u'weather'][0][u'description']),
            'country': str(weather_data[u'sys']['country']),
            'city': str(weather_data[u'name']),
            'temp_high': str(weather_data[u'main'][u'temp_max']),
            'temp_low': str(weather_data[u'main'][u'temp_min']),
            'temp_curr':  str(weather_data[u'main'][u'temp']),
    }
    if info.has_key(u'rain'):
        info['rain1h'] = str(weather_data[u'rain'][u'1h']) # Hourly Precipitation
    return info
 
def _getWeather(location):
    ''' @param location string: of form 'City,Country Code' 
                                eg. 'Christchurch,NZ'
        @returns: JSON object containing weather data for the given location.
    '''
    return _extractUseful(json.loads(requests.get(WEATHER_URL.format(location)).content))

def GetWeather(loc):
    # Safe call for getweather
    #return _getWeather(loc)
    try:
        return _getWeather(loc)
    except:
        print "Error getting weather for {0}. \n".format(loc)

class openweathermap_tests(unittest.TestCase):
  def test_basic(self):
      self.assertIsNotNone(GetWeather('New York, USA'))
      weather = GetWeather('New York, USA')
      self.assertTrue(weather['city'], 'New York')

if __name__ == '__main__':
    unittest.main()
