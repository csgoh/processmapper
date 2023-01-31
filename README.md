[![license](https://img.shields.io/badge/license-mit-brightgreen.svg?style=plastic)](https://en.wikipedia.org/wiki/MIT_License)
[![CodeFactor](https://www.codefactor.io/repository/github/csgoh/processmapper/badge)](https://www.codefactor.io/repository/github/csgoh/processmapper)
![code size](https://img.shields.io/github/languages/code-size/csgoh/processmapper?style=plastic)

# ProcessMapper

This is a python library to generate business process diagram using code. The intention is adhere to BPMN notation.

It is still under development :construction:

Any ideas or suggestions, please send it to me via [GitHub Discussions](https://github.com/csgoh/processmapper/discussions).

You can see the sample code and output for design concept below.

```python
from processmapper.lane import EventType, ActivityType, GatewayType
from processmapper.processmap import ProcessMap


with ProcessMap(1150, 220) as my_process_map:
    with my_process_map.add_lane("Application \nUser") as lane1:
        start = lane1.add_element("Start", EventType.START)
        login = lane1.add_element("Login", ActivityType.TASK)
        search_records = lane1.add_element("Search Records", ActivityType.TASK)
        result_found = lane1.add_element("Result Found?", GatewayType.EXCLUSIVE)
        display_result = lane1.add_element("Display Result", ActivityType.TASK)
        logout = lane1.add_element("Logout", ActivityType.TASK)
        end = lane1.add_element("End", EventType.END)

        start.connect(login).connect(search_records).connect(result_found)
        result_found.connect(display_result).connect(logout).connect(end)
        result_found.connect(search_records)
      
    my_process_map.draw()
    my_process_map.save("my_process_map_demo.png")
```

![Process Map](https://github.com/csgoh/processmapper/blob/main/my_process_map_demo.png)
