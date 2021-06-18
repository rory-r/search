<?php
ini_set('display_errors', '1');
ini_set('display_startup_errors', '1');
error_reporting(E_ALL);
if(isset($_POST['text'])){
	$data = file_get_contents("./elasticsearch.txt", filesize("./elasticsearch.txt"));
	$pos = strpos($data, "\n");
	$userpwd = substr($data, 0, $pos);
	$deployment = substr($data, $pos+1);
    $json = '{"query": {"match": {"html":'.str_replace("\u0022","\\\\\"",json_encode( $_POST['text'] ,JSON_HEX_QUOT)).'}}}';
    $ch = curl_init($deployment."/_search?pretty&size=10");
    curl_setopt( $ch, CURLOPT_POST, 1 );
    curl_setopt( $ch, CURLOPT_RETURNTRANSFER, true );
    curl_setopt( $ch, CURLOPT_POSTFIELDS, $json );
    $headers = ["X-HTTP-Method-Override: GET", "Content-Type: application/json",];
    curl_setopt( $ch, CURLOPT_HTTPHEADER, $headers );
    curl_setopt( $ch, CURLOPT_TIMEOUT, 150 );
    curl_setopt($ch, CURLOPT_USERPWD, $userpwd);
    curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
    $result = curl_exec($ch);
    if(curl_error($ch)) {
        echo curl_error($ch);
    }
    else{
        $j = json_decode($result, JSON_NUMERIC_CHECK);
        $hits = $j["hits"]["total"]["value"];
        for($i = 0; $i <= $hits && $i < 10; $i++){
            echo '<a href="#'.$i.'">'.$i.'</a>&nbsp;&nbsp;';
        }
        echo '<br>';
        echo $hits." results in ".$j["took"]." seconds.<br>";
        for($i = 0; $i <= $hits && $i < 10; $i++){
            $html = $j["hits"]["hits"][0]["_source"]["html"];
            echo '<div id="'.$i.'">'.str_replace('\\n|\\t', '', $html).'</div><br>';
        }
    }
    curl_close($ch);
    exit();
}

echo '
<html>
    <head>
        <title>Search</title>
        <script src="interface.js"></script>
        <link rel="stylesheet" href="interface.css">
    </head>
    <body>
        <div id="searchdiv">
            <h1>Search</h1>
            <div id="searchbar">
                <svg focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path id="icon" d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"></path></svg>
                <input placeholder = "Search" type="text" onkeydown="search(this)"/>
            </div>
        </div>
        <div id="results"></div>
        <div id="credit">by Rory Russell</div>
    </body>
</html>';
?>