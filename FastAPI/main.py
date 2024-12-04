# main.py
from fastapi import FastAPI, HTTPException, Depends, WebSocket
from fastapi.responses import JSONResponse  # Add this import for JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from models import User, Login, Token, TokenData, CommandRequest, EmailModel  # Adjust the import based on your file structure
from database import users, create_user, find_user_by_email, Hash, send_verification_email
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
import pyvisa
from pyvisa import ResourceManager, VisaIOError
import time
from mail import mail, create_message
from itsdangerous import URLSafeTimedSerializer
import logging
from fastapi import BackgroundTasks
from utils import create_url_safe_token
from motor.motor_asyncio import AsyncIOMotorClient
from utils import serializer  # Ensure serializer is properly imported

# FastAPI initialization
app = FastAPI()

# CORS setup
origins = [
    "http://localhost:3000",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Token setup
SECRET_KEY = "URgbP75FiM!YkZPF535UZPucsUR*G8*@zt"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()  # Copy input data
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  # Update expiration time
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#token validation
@app.get("/verify/{token}")
async def verify_email(token: str):
    try:
        # Decode the token and get the email
        decoded_data = decode_url_safe_token(token)  # Assuming your decoding logic here
        email = decoded_data.get("email")

        # Ensure email exists in the database
        print(f"Finding user with email: {email}")
        user = await users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # If the user is already verified, return an appropriate message
        if user.get("is_verified"):
            return JSONResponse(content={"message": "Email already verified!"})

        # Update the user to mark them as verified
        await users.update_one({"email": email}, {"$set": {"is_verified": True}})

        return JSONResponse(content={"message": "Email successfully verified!"})

    except Exception as e:
        logging.error(f"Error during email verification: {e}")
        raise HTTPException(status_code=400, detail="Invalid or expired token")

# OAuth2 scheme for token authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Check if the token is valid to return user info
async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return verify_token(token, credentials_exception)

def decode_url_safe_token(token:str):
    try:
        token_data = serializer.loads(token)

        return token_data
    
    except Exception as e:
        logging.error(str(e))
        
# Registration endpoint
@app.post("/register")
async def register_user(request: User, bg_tasks: BackgroundTasks):
    return await create_user(request, bg_tasks)

# Login endpoint
@app.post("/login")
async def login(request: OAuth2PasswordRequestForm = Depends()):
    # Find user by email
    user = await find_user_by_email(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="No user found with this email")

    # Check if the user's email is verified
    if not user.get("is_verified", False):  # Assuming 'is_verified' is a field in your user document
        raise HTTPException(status_code=400, detail="Email not verified. Please check your inbox to verify your email.")

    # Check if the password is correct
    if not Hash.verify(user["password"], request.password):
        raise HTTPException(status_code=403, detail="Incorrect email or password")

    # Create access token
    access_token = create_access_token(data={"sub": user["email"]})
    
    return {"access_token": access_token, "token_type": "bearer"}

sleep_timer = 1

# WebSocket Endpoint for real-time communication
@app.websocket("/ws/test/{test_id}")
async def websocket_endpoint(websocket: WebSocket, test_id: str):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Test {test_id}: {data}")

def connect_to_power_supply():
    rm = pyvisa.ResourceManager()
    try:
        
        power_supply = rm.open_resource('USB0::0x1AB1::0x0E11::DP8A253700506::INSTR')  # Replace with actual VISA address
        #power_supply = rm.open_resource('ASRL1::INSTR')
        print(f"Inside power supply")
        return power_supply
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def set_channel_voltage(channel: int, voltage: float):
    try:
        # Try to connect to the power supply
        print(f"Before connection")
        power_supply = connect_to_power_supply()

        # Check if the connection is valid
        if not power_supply:
            raise HTTPException(status_code=500, detail="Failed to connect to power supply.")

        print(f"Power supply connected: {power_supply}")

        # Send the command to select the channel
        chstring = f'INST CH{channel}'
        print(f"Sending command to power supply: {chstring}")
        power_supply.write(chstring)

        # Send the voltage value
        vstring = f'VOLT {voltage}'
        print(f"Sending voltage value to power supply: {vstring}")
        power_supply.write(vstring)

        # Turn on the output for the channel
        outstring = f'OUTP CH{channel},ON'
        print(f"Sending output command to power supply: {outstring}")
        power_supply.write(outstring)

        # Return the success message
        return f"Channel {channel} Voltage set to {voltage}"

    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while setting the channel voltage.")


#class MockPowerSupply:
    #def write(self, command: str):
       # print(f"Mock Power Supply received command: {command}")

#def connect_to_power_supply():
    # Return a mock power supply object for testing
    #return MockPowerSupply()

def set_channel_current(channel: int, current: float):
    try:
        print("Made it here")
        power_supply = connect_to_power_supply()

        # Check if the connection is valid
        if not power_supply:
            raise HTTPException(status_code=500, detail="Failed to connect to power supply.")

        print(f"Power supply connected: {power_supply}")

        # Send the command to set the channel
        chstring = f'INST CH{channel}'
        print(f"Sending command to power supply: {chstring}")
        power_supply.write(chstring)

        # Send the current value
        cstring = f'CURR {current}'
        print(f"Sending current value to power supply: {cstring}")
        power_supply.write(cstring)

        # Turn on the output for the channel
        outstring = f'OUTP CH{channel},ON'
        print(f"Sending output command to power supply: {outstring}")
        power_supply.write(outstring)

        print("made it here too")
        return f"Channel {channel} Current set to {current}"
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while setting the channel current.")

# Similar adjustments to other endpoints to ensure they return a "message" field


def get_channel_voltage(channel:int):
    power_supply = connect_to_power_supply()
    vol = power_supply.query('MEAS:VOLT? CH' + str(channel))
    return vol

def get_channel_current(channel:int):
    power_supply = connect_to_power_supply()
    curr = power_supply.query('MEAS:CURR? CH' + str(channel))
    return curr

def connect_to_multimeter():
    rm = pyvisa.ResourceManager()
    try:
        multimeter = rm.open_resource('USB0::62700::4614::SDM35HBQ7R1319::0::INSTR')
        return multimeter
    except pyvisa.VisaIOError as e:
        print("Connection error:", e)
        raise HTTPException(status_code=500, detail=str(e))

def measure_voltage():
    multimeter = connect_to_multimeter()
    if multimeter:
        multimeter.write(":MEAS:VOLT:DC?")
        voltage = multimeter.read()
        return float(voltage)
        #return {f"Measured Voltage: {voltage} V"}
    else:
        print("Multimeter connection not available.")

def measure_current():
    multimeter = connect_to_multimeter()
    if multimeter:
        multimeter.write(":MEAS:CURR:DC?")
        current = multimeter.read()
        return float(current)
        #return {f"Measured Current: {current} A"}
    else:
        print("Multimeter connection not available.")

def measure_continuity():
    multimeter = connect_to_multimeter()
    if multimeter:
        multimeter.write(":MEAS:CONT?")
        continuity = multimeter.read()
       
        # Interpret the result if necessary
        if continuity.strip() == "1":  # Adjust based on your multimeter's response
            return {"Continuity": "Closed (Continuity detected)"}
        else:
            return {"Continuity": "Open (No continuity)"}
    else:
        print("Multimeter connection not available.")


@app.post("/dashboard")
async def process_commands(request: CommandRequest):
    responses = []

    for q in request.commands:
        # Handle SETV command
        if q[:4] == 'SETV':
            parts = q.strip().split(',')
            if len(parts) == 2:
                try:
                    # Extract the channel and voltage values by stripping extra spaces
                    channel = int(parts[0].strip().split()[1])  # Get channel after the 'TSTV' keyword
                    voltage = float(parts[1].strip())  # Get the voltage value after the comma
                    print(f"Received Channel: {channel}")
                    print(f"Received Voltage: {voltage}")

                    # Validate the channel
                    if channel < 1 or channel > 3:
                        raise HTTPException(status_code=400, detail="Channel must be 1, 2, or 3.")

                    # Call the function to set the channel voltage
                    response = set_channel_voltage(channel, voltage)
                    print(f"response: {response}")
                    responses.append(response)

                except ValueError:
                    responses.append("Error processing SETV command: Invalid input values. Channel and voltage must be valid numbers.")
            else:
                responses.append("Error processing SETV command: Invalid command format. Expected 'SETV <channel>, <voltage>'.")
        
        elif q[:4] == 'SSSS':
            rm = pyvisa.ResourceManager()
            print(rm.list_resources())

            #responses.append(measure_voltage())
        # Handle SETC command
        elif q[:4] == 'SETC':
            print(f"Received query: {q}")
            parts = q.strip().split(',')
            if len(parts) == 2:
                try:
                    channel = int(parts[0].strip().split()[1])  # Get channel after the 'SETC' keyword
                    current = float(parts[1].strip())  # Get the current value after the comma
                    if channel < 1 or channel > 3:
                        raise HTTPException(status_code=400, detail="Channel must be 1, 2, or 3.")
                    response = set_channel_current(channel, current)
                    responses.append(response)
                except ValueError:
                    responses.append("Error processing SETC command: Invalid input values.")
            else:
                responses.append("Error processing SETC command: Invalid command format. Expected 'SETC <channel>, <current>'.")
        
        # Handle GETV command
        elif q[:4] == 'GETV':
            try:
                vals = re.findall(r'\d', q)[:1]
                ch = int(vals[0])
                if ch > 3 or ch < 1:
                    responses.append("Error processing GETV command: channel must be 1, 2, or 3")
                else:
                    vol = get_channel_voltage(ch)
                    responses.append(f"Voltage at channel {ch}: {vol}")
            except:
                responses.append("Error processing GETV command: Invalid channel.")

        # Handle GETC command
        elif q[:4] == 'GETC':
            vals = re.findall(r'\d', q)[:1]
            ch = int(vals[0])
            if ch > 3 or ch < 1:
                responses.append("Error processing GETC command: channel must be 1, 2, or 3")
            else:
                curr = get_channel_current(ch)
                responses.append(f"Current at channel {ch}: {curr}")

        # Handle TSTV command
        elif q[:4] == 'TSTV':
            print(f"Received query: {q}")
            # Split the command into parts
            parts = q.strip().split(',')
            if len(parts) == 3:
                try:
                    # Extract the channel and voltage values by stripping extra spaces
                    voltage = float(parts[0].strip().split()[1])  # get voltage 
                    minimum = float(parts[1].strip())  # get min after comma 
                    maximum = float(parts[2].strip()) # get max after comma 
                    print(f"Received Voltage: {voltage}")
                    print(f"Received Minimum: {minimum}")
                    print(f"Received Maximum: {maximum}")
                    
                    channel = 1
                    # validate the channel
                    if channel < 1 or channel > 3:
                        raise HTTPException(status_code=400, detail="Channel must be 1, 2, or 3.")

                    # Call the function to set the channel voltage
                    #response = set_channel_voltage(channel, voltage)
                    set_channel_voltage(channel, voltage)
                    time.sleep(1)
                    readV = measure_voltage()
                    
                    if (readV > maximum or readV < minimum):
                        passVal = False
                        response = {f"Measured voltage: {readV}V, Test Failed"}
                    else:
                        passVal = True
                        response = {f"Measured Voltage: {readV}V, Test Passed"}
                         
                    
                    print(f"response: {response}")
                    responses.append(response)

                except ValueError:
                    responses.append("Error processing TSTV command: Invalid input values.")
            else:
                responses.append("Error processing TSTV command: Invalid command format. Expected 'TSTV <voltage>, <minimum>, <maximum>'.")


        # Handle TSTC command
        elif q[:4] == 'TSTC':
            print(f"Received query: {q}")
            # Split the command into parts
            parts = q.strip().split(',')
            if len(parts) == 3:
                try:
                    # Extract the channel and voltage values by stripping extra spaces
                    current = float(parts[0].strip().split()[1])  # get voltage 
                    minimum = float(parts[1].strip())  # get min after comma 
                    maximum = float(parts[2].strip()) # get max after comma 
                    print(f"Received Voltage: {current}")
                    print(f"Received Minimum: {minimum}")
                    print(f"Received Maximum: {maximum}")
                    
                    channel = 1
                    # validate the channel
                    if channel < 1 or channel > 3:
                        raise HTTPException(status_code=400, detail="Channel must be 1, 2, or 3.")

                    # Call the function to set the channel voltage
                    #response = set_channel_voltage(channel, voltage)
                    set_channel_current(channel, current)
                    time.sleep(1)
                    readC = measure_current()
                    
                    if (readC > maximum or readC < minimum):
                        passVal = False
                        response = {f"Measured current: {readC}A, Test Failed"}
                    else:
                        passVal = True
                        response = {f"Measured current: {readC}A, Test Passed"}
                         
                    print(f"response: {response}")
                    responses.append(response)

                except ValueError:
                    responses.append("Error processing TSTV command: Invalid input values.")
            else:
                responses.append("Error processing TSTV command: Invalid command format. Expected 'TSTV <voltage>, <minimum>, <maximum>'.")


        # Handle TSCO command
        elif q[:4] == 'TSCO':
            responses.append(measure_continuity())

        # Handle TSTR command
        elif q[:4] == 'TSTR':
            multimeter = connect_to_multimeter()
            if multimeter:
                multimeter.write(":MEAS:RES?")
                resistance = multimeter.read()
                responses.append(f"Resistance: {resistance} Ohms")
            else:
                responses.append("Error processing TSTR command: multimeter not found")

        # Handle PRBV command
        elif q[:4] == 'PRBV':
            responses.append("PROBING VOLTAGE")

        # Handle PRBC command
        elif q[:4] == 'PRBC':
            responses.append("PROBING CURRENT")

        # If command not found
        else:
            responses.append(f"Error processing command '{q}': command not found")

    # Return all responses as a list of strings
    return {"responses": responses}

