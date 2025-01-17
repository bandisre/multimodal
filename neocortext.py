import pyrealsense2 as rs
import numpy as np
import cv2
import os

current_dir = os.getcwd()

pipe = rs.pipeline()
cfg  = rs.config()

cfg.enable_stream(rs.stream.color, 640,480, rs.format.bgr8, 30)
cfg.enable_stream(rs.stream.depth, 640,480, rs.format.z16, 30)

pipe.start(cfg)

while True:
    frame = pipe.wait_for_frames()
    depth_frame = frame.get_depth_frame()
    color_frame = frame.get_color_frame()

    depth_image = np.asanyarray(depth_frame.get_data())
    color_image = np.asanyarray(color_frame.get_data())
    depth_cm = cv2.applyColorMap(cv2.convertScaleAbs(depth_image,
                                     alpha = 0.5), cv2.COLORMAP_JET)

    gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

    cv2.imshow('rgb', color_image)
    cv2.imshow('depth', depth_cm)

    if cv2.waitKey(1) == ord('q'):
        file_name = "color_frame.jpg"
        file_path = os.path.join(current_dir, file_name)
        cv2.imwrite(file_path, color_image)

        # LAVIS
        import torch
        from PIL import Image
        # setup device to use
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # load sample image
        raw_image = Image.open("color_frame.jpg").convert("RGB")
        from lavis.models import load_model_and_preprocess
        model, vis_processors, _ = load_model_and_preprocess(name="blip_caption", model_type="base_coco", is_eval=True, device=device)
        # preprocess the image
        # vis_processors stores image transforms for "train" and "eval" (validation / testing / inference)
        image = vis_processors["eval"](raw_image).unsqueeze(0).to(device)
        # generate caption
        description = model.generate({"image": image})
        f = open("description.txt", "a")
        f.write("".join(description))
        f.write("\n")
        f.close()

        break

pipe.stop()