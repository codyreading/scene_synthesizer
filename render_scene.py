import pybullet as p
import pybullet_data
import numpy as np
import time
import math
from moviepy import ImageSequenceClip
from tqdm import tqdm
import os


# Connect to the physics server in DIRECT mode (no GUI)
physicsClient = p.connect(p.DIRECT)

# Set gravity
p.setGravity(0, 0, -9.81)

# Set the search path to find URDF files
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# Load a plane
planeId = p.loadURDF("scene.urdf")

startPos = [0.0, 1.0, -0.5]  # 1 meter along x-axis, on the ground
startOrientation = p.getQuaternionFromEuler([0, 0, 0])
robotId = p.loadURDF("kuka_iiwa/model.urdf", startPos, startOrientation, useFixedBase=1)

# Set the robot to a more natural pose
# Get the number of joints
numJoints = p.getNumJoints(robotId)

# Define a more natural pose - slight bends in the joints
# For KUKA iiwa, we'll create a slight curve or "ready position"
natural_positions = [0, math.pi/6, 0, -math.pi/4, 0, math.pi/3, 0]  # Example angles

# Apply the joint positions
for i in range(min(len(natural_positions), numJoints)):
    p.resetJointState(robotId, i, natural_positions[i])

# Function to render 360 views
def render_360_view(robotId, num_frames=36, distance=3.0, height=1.0, width=640, height_px=480, scene_center=[0, 0, 0]):
    """
    Renders a 360-degree view around the robot.

    Args:
        robotId: PyBullet robot ID
        num_frames: Number of frames in the 360-degree view
        distance: Distance from the robot
        height: Height of the camera relative to robot base
        width, height_px: Resolution of the rendered image
    """

    # Create an array to store all frames
    frames = []

    # Render views from different angles
    for i in tqdm(range(num_frames), desc="Rendering Frames"):
        # Calculate angle and position
        angle = 2 * math.pi * i / num_frames
        x = scene_center[0] + distance * math.cos(angle)
        y = scene_center[1] + distance * math.sin(angle)
        z = scene_center[2] + height

        # Camera target at robot position

        # Set view matrix (camera position)
        view_matrix = p.computeViewMatrix(
            cameraEyePosition=[x, y, z],
            cameraTargetPosition=scene_center,
            cameraUpVector=[0, 0, 1]
        )

        # Set projection matrix
        projection_matrix = p.computeProjectionMatrixFOV(
            fov=60.0,
            aspect=width/height_px,
            nearVal=0.1,
            farVal=100.0
        )

        # Get the image
        (_, _, rgb_img, _, _) = p.getCameraImage(
            width=width,
            height=height_px,
            viewMatrix=view_matrix,
            projectionMatrix=projection_matrix,
            renderer=p.ER_BULLET_HARDWARE_OPENGL
        )

        # Convert the RGB data to an image (keep as RGB for MoviePy)
        rgb_img = np.reshape(rgb_img, (height_px, width, 4))[:, :, :3]
        frames.append(rgb_img)

        # Step the simulation
        p.stepSimulation()

    return frames

# Run the simulation for a few steps to let things settle
for i in range(10):
    p.stepSimulation()

# Render the 360-degree view
frames = render_360_view(robotId, num_frames=72)  # Increased to 72 for smoother rotation

# Create a video using MoviePy
print("Creating video...")
clip = ImageSequenceClip([frame for frame in frames], fps=15)

# Export as MP4 (higher quality than AVI)
clip.write_videofile("360_view.mp4", codec="libx264")

# Export as GIF for easy viewing (optional)
clip.write_gif("360_view.gif", fps=15)

print("Rendering complete. Video saved as '360_view.mp4' and '360_view.gif'")

# Disconnect when done
p.disconnect()