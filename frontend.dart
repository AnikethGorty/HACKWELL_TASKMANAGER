import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:web_socket_channel/io.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';

void main() {
  runApp(TaskAllocatorApp());
}

class TaskAllocatorApp extends StatefulWidget {
  @override
  _TaskAllocatorAppState createState() => _TaskAllocatorAppState();
}

class _TaskAllocatorAppState extends State<TaskAllocatorApp> {
  bool isDarkMode = false;

  void toggleDarkMode() {
    setState(() {
      isDarkMode = !isDarkMode;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: isDarkMode ? ThemeData.dark() : ThemeData.light(),
      home: WelcomeScreen(toggleDarkMode: toggleDarkMode, isDarkMode: isDarkMode),
    );
  }
}

class WelcomeScreen extends StatelessWidget {
  final Function toggleDarkMode;
  final bool isDarkMode;
  WelcomeScreen({required this.toggleDarkMode, required this.isDarkMode});

  final TextEditingController nameController = TextEditingController();

  void navigateToDashboard(BuildContext context) {
    if (nameController.text.isNotEmpty) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => TaskAllocatorScreen(
            userName: nameController.text,
            toggleDarkMode: toggleDarkMode,
            isDarkMode: isDarkMode,
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Task Allocator"),
        actions: [
          IconButton(
            icon: Icon(isDarkMode ? Icons.wb_sunny : Icons.nightlight_round),
            onPressed: () => toggleDarkMode(),
          )
        ],
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text("Enter Your Name", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
              SizedBox(height: 10),
              TextField(
                controller: nameController,
                decoration: InputDecoration(border: OutlineInputBorder(), labelText: "Your Name"),
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: () => navigateToDashboard(context),
                child: Text("Proceed"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class TaskAllocatorScreen extends StatefulWidget {
  final String userName;
  final Function toggleDarkMode;
  final bool isDarkMode;
  TaskAllocatorScreen({required this.userName, required this.toggleDarkMode, required this.isDarkMode});

  @override
  _TaskAllocatorScreenState createState() => _TaskAllocatorScreenState();
}

class _TaskAllocatorScreenState extends State<TaskAllocatorScreen> {
  final WebSocketChannel channel = IOWebSocketChannel.connect("ws://localhost:8765");
  
  List<Map<String, dynamic>> tasks = [];
  TextEditingController taskNameController = TextEditingController();
  TextEditingController skillsController = TextEditingController();
  DateTime? selectedDeadline;
  String serverResponse = "";

  @override
  void initState() {
    super.initState();
    channel.stream.listen((message) {
      setState(() {
        serverResponse = "Server Response: $message";
      });
    });
  }

  void sendTaskToServer() {
    if (taskNameController.text.isNotEmpty && selectedDeadline != null) {
      Map<String, dynamic> taskData = {
        "task_name": taskNameController.text,
        "deadline": DateFormat('yyyy-MM-dd').format(selectedDeadline!),
        "skills": skillsController.text.split(",").map((s) => s.trim()).toList(),
      };
      
      String jsonTask = jsonEncode(taskData);
      channel.sink.add(jsonTask);

      setState(() {
        tasks.add(taskData);
        taskNameController.clear();
        skillsController.clear();
        selectedDeadline = null;
      });
    }
  }

  Future<void> selectDeadline(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime.now(),
      lastDate: DateTime(2101),
    );
    if (picked != null) {
      setState(() {
        selectedDeadline = picked;
      });
    }
  }

  @override
  void dispose() {
    channel.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Welcome, ${widget.userName}"),
        actions: [
          IconButton(
            icon: Icon(widget.isDarkMode ? Icons.wb_sunny : Icons.nightlight_round),
            onPressed: () => widget.toggleDarkMode(),
          )
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: taskNameController,
              decoration: InputDecoration(labelText: "Task Name", border: OutlineInputBorder()),
            ),
            SizedBox(height: 10),
            TextField(
              controller: skillsController,
              decoration: InputDecoration(labelText: "Skills (comma-separated)", border: OutlineInputBorder()),
            ),
            SizedBox(height: 10),
            Row(
              children: [
                Text(selectedDeadline == null
                    ? "Select Deadline"
                    : "Deadline: ${DateFormat('yyyy-MM-dd').format(selectedDeadline!)}"),
                IconButton(
                  icon: Icon(Icons.calendar_today),
                  onPressed: () => selectDeadline(context),
                ),
              ],
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: sendTaskToServer,
              child: Text("Send Task to Server"),
            ),
            SizedBox(height: 20),
            Text(serverResponse, style: TextStyle(color: Colors.green)),
          ],
        ),
      ),
    );
  }
}
