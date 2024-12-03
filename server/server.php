<?php
// server.php

// Allow cross-origin requests
header('Access-Control-Allow-Origin: *');
header('Content-Type: application/json');

// Files to store the data (simple persistence for demo purposes)
$messageFile = 'client_messages.json';
$presetFile = 'preset_data.json';

// Define preset data
$presetData = [
    'speed' => 100,
    'radius' => 20,
    'a' => 1.00001,
    'max_fps' => 60,
    'boost_count' => 70,
    'world_size' => 800,
];

// Ensure preset data is saved (if not already)
if (!file_exists($presetFile)) {
    file_put_contents($presetFile, json_encode($presetData));
}

// Check if the request method is POST (to save client message)
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);

    if ($data && isset($data['client_id']) && isset($data['message'])) {
        // Read existing messages
        $storedMessages = [];
        if (file_exists($messageFile)) {
            $storedMessages = json_decode(file_get_contents($messageFile), true);
        }

        // Save the new message under the client's ID
        $storedMessages[$data['client_id']] = $data['message'];
        file_put_contents($messageFile, json_encode($storedMessages));

        echo json_encode(['status' => 'success', 'message' => 'Message saved']);
    } else {
        echo json_encode(['status' => 'error', 'message' => 'Invalid data']);
    }
} 
// Check if the request method is GET (to retrieve data)
elseif ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (isset($_GET['client_id'])) {
        $client_id = $_GET['client_id'];

        // Read stored messages
        $storedMessages = [];
        if (file_exists($messageFile)) {
            $storedMessages = json_decode(file_get_contents($messageFile), true);
        }

        // Remove the client's own message
        unset($storedMessages[$client_id]);

        // Read preset data
        $presetData = [];
        if (file_exists($presetFile)) {
            $presetData = json_decode(file_get_contents($presetFile), true);
        }

        // Return preset data and other clients' messages
        $response = [
            'preset_data' => $presetData,
            'message' => $storedMessages,
        ];

        echo json_encode($response);
    } else {
        echo json_encode(['status' => 'error', 'message' => 'Client ID is required']);
    }
} else {
    echo json_encode(['status' => 'error', 'message' => 'Invalid request method']);
}
?>
