import React, { useState, useRef, useEffect } from "react";
import { Button, Box, AppBar, Toolbar, Typography, IconButton, Menu, MenuItem } from "@mui/material";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import './ButtonStyles.css';
import './global.css';
import './textbox.css'; // Additional CSS for line numbering

const Dashboard = () => {
 const [anchorEl, setAnchorEl] = useState(null);
 const [text, setText] = useState("");
 const [activeLine, setActiveLine] = useState(null);
 const [statusMessage, setStatusMessage] = useState('');  // New state for status message
 const textareaRef = useRef(null);
 const lineNumbersRef = useRef(null);

 const handleProfileMenuOpen = (event) => {
   setAnchorEl(event.currentTarget);
 };


 const handleMenuClose = () => {
   setAnchorEl(null);
 };

 const handleTextChange = (event) => {
   setText(event.target.value);
 };

 const handleLineClick = (lineIndex) => {
   setActiveLine(lineIndex);
 };

 // Create an array of line numbers based on the number of lines in the text area
 const lines = text.split("\n");
 const numberOfLines = lines.length;
 const lineNumbers = Array.from({ length: numberOfLines }, (_, index) => index + 1);

 // Sync scroll positions of line numbers and text area
 useEffect(() => {
   const textarea = textareaRef.current;
   const lineNumbers = lineNumbersRef.current;

   const syncScroll = (source, target) => {
     target.scrollTop = source.scrollTop;
   };

   const handleScroll = (event) => {
     if (event.target === textarea) {
       syncScroll(textarea, lineNumbers);
     } else {
       syncScroll(lineNumbers, textarea);
     }
   };
   textarea.addEventListener("scroll", handleScroll);
   lineNumbers.addEventListener("scroll", handleScroll);

   return () => {
     textarea.removeEventListener("scroll", handleScroll);
     lineNumbers.removeEventListener("scroll", handleScroll);
   };
 }, []);

 const handleRunClick = async () => {
   try {
     // Split the input into multiple commands based on newline
     const commandList = text.split('\n').map((command) => command.trim());  // Trim any extra spaces

     // Make a POST request to the FastAPI backend with the command list as the payload
     const response = await fetch("http://localhost:8000/dashboard", {
       method: "POST",
       headers: {
         "Content-Type": "application/json",
       },
       body: JSON.stringify({ commands: commandList }), // Send commands array
     });

     if (response.ok) {
       const result = await response.text();  // Use .text() to handle string response
       console.log("Backend Response:", result);  // Log the response

       // Set the status message to the result from the backend
       setStatusMessage(result);  // Display the response in the terminal
     } else {
       const errorResult = await response.json();
       console.error("Error with the backend request", errorResult);
 
       // Ensure we're only rendering a string message
       const errorMessage = errorResult?.msg || errorResult?.detail || 'Failed to process command.';
       setStatusMessage(errorMessage);
     }
   } catch (error) {
     console.error("Error:", error);
     setStatusMessage('An error occurred while contacting the backend.');
   }
 };

 

 return (
   <Box sx={{ display: "flex", flexDirection: "column", height: "100vh", margin: 0, backgroundColor: "#323232", width: "100%" }}>
     <AppBar position="static" sx={{ backgroundColor: '#0C4459', width: "100%" }} className="MuiAppBar-root">
       <Toolbar>
         <Typography variant="h6" className="MuiTypography-root">
           PCB Debugger
         </Typography>
         <Box sx={{ display: "flex", flexGrow: 1, justifyContent: "flex-start" }}>
           <Button className="button" onClick={handleRunClick}>Run</Button>
           <Button className="button">Stop</Button>
           <Button className="button">Troubleshoot Guide</Button>
           <Button className="button">Save Session</Button>
           <Button className="button">Past Sessions</Button>
         </Box>
         <IconButton color="inherit" onClick={handleProfileMenuOpen}>
           <AccountCircleIcon />
         </IconButton>
         <Menu
           anchorEl={anchorEl}
           open={Boolean(anchorEl)}
           onClose={handleMenuClose}
           anchorOrigin={{
             vertical: "top",
             horizontal: "right",
           }}
           transformOrigin={{
             vertical: "top",
             horizontal: "right",
           }}
         >
           <MenuItem onClick={handleMenuClose}>Profile</MenuItem>
           <MenuItem onClick={handleMenuClose}>Settings</MenuItem>
           <MenuItem onClick={handleMenuClose}>Logout</MenuItem>
         </Menu>
       </Toolbar>
     </AppBar>
     <Box sx={{ display: "flex", flexGrow: 1, backgroundColor: "#323232", height: "100%", width: "100%" }}>
       {/* Main Content */}
       <Box className="textarea-container">
         {/* Line Numbers */}
         <Box className="line-numbers" ref={lineNumbersRef}>
           {lineNumbers.map((lineNumber, index) => (
             <Typography
               key={index}
               onClick={() => handleLineClick(index)}
               sx={{ marginBottom: '0px', marginTop: '0px', paddingBottom: '0px', lineHeight: '1', fontSize: '22px', paddingLeft: '15px', paddingRight: '10px' }}
               className={activeLine === index ? "active-line" : ""}
             >
               {lineNumber}
             </Typography>
           ))}
         </Box>
         {/* Text Area with input */}
         <textarea
           ref={textareaRef}
           value={text}
           onChange={handleTextChange}
           className="textarea"
           rows={20}
         />
       </Box>
       {/* Graphs Section */}
       <Box className="graphs-section">
         <Typography variant="h6" sx={{ textAlign: "center", width: "100%" }}>PCB Results</Typography>
         <Box sx={{ height: "100%", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
           <Box className="graphs-container">
             <Typography className="graph-placeholder" variant="body1">Graphs will be displayed here</Typography>
           </Box>
         </Box>
       </Box>
     </Box>
     {/* Status Message Box */}
     <Box sx={{
       display: 'flex',
       justifyContent: 'flex-start',  // Aligns horizontally to the left
       alignItems: 'flex-start',       // Aligns vertically to the top
       border: "1px solid #000",
       overflowY: "auto",
       backgroundColor: "#000",
       color: "#fff",
       height: "175px",  // Ensure it takes the full height of the viewport (optional)
       fontFamily: 'Courier New, Courier, monospace', // Terminal-like font style
     }}>
       <Typography variant="body2">{statusMessage}</Typography>
     </Box>
   </Box>
 );
};

export default Dashboard;
