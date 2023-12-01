import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const MyApp());
}
class MyApp extends StatefulWidget {
  const MyApp({Key? key}) : super(key: key);
  @override
  State<MyApp> createState() => _MyAppState();
}
class _MyAppState extends State<MyApp> {
  late String cpos = 'NAN';
  late Position home =  Position(longitude: 0, latitude: 0, timestamp:DateTime(2023,07,02), accuracy: 0, altitude: 0, altitudeAccuracy: 0, heading: 0, headingAccuracy: 0, speed: 0, speedAccuracy: 0);

  Future<http.Response> locationAPI(bool home) {
    return http.post(
      Uri.parse('http://192.168.1.13:5000/location'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(<String, bool>{
        'location': home,
      }),
    );
  }

  void uploadToConnector(bool home)async{
    var res = await locationAPI(home);
    print(res.statusCode);
  }

  void fetchLocation() async{
    Position position = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high);
    print(position);
    print(home);
    print('-'*10);
    if (cpos == 'NAN') {
        home = position;
      }
      setState(() {
        if (home.longitude == position.longitude && home.latitude == position.latitude && cpos != 'HOME'){
          cpos = 'HOME';
          uploadToConnector(true);
        }
        else if(home.longitude != position.longitude && home.latitude != position.latitude){
          uploadToConnector(false);
          cpos = 'AWAY';
        }
      });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hello World Demo Application',
      theme: ThemeData(
        primarySwatch: Colors.lightGreen,
      ),
      home: Scaffold(
        appBar: AppBar(
          title: Text('Location AXIE'),
        ),
        // Sets the content to the
        // center of the application page
        body: Center(
          // Sets the content of the Application
            child: Column(
              children: [
                Text(
                  'Location Transmitor ...$cpos \n HOME : ${home.latitude} | ${home.longitude}',
                ),
                SizedBox(height: 20),
                ElevatedButton(onPressed: (){
                  fetchLocation();
                }, child: Text("Location Update !"))
              ],
            ),),
      ),
    );
  }
}


