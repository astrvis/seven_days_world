import sys
from dataclasses import dataclass
from typing import List, Literal, Optional, Tuple, TypedDict

import cv2
import mss
import numpy as np
from rapidocr import EngineType, LangDet, LangRec, ModelType, OCRVersion, RapidOCR


class Fish_ocr:
    def __init__(self):
        super().__init__()
        self.ocr = None
        # self.init_ocr()
        self._load_done = False

    def _init_ocr(self):
        try:
            self.ocr = RapidOCR(
                params={
                    "Det.engine_type": EngineType.TORCH,
                    "Det.lang_type": LangDet.CH,
                    "Det.model_type": ModelType.SMALL,
                    "Det.ocr_version": OCRVersion.PPOCRV6,
                    "Rec.engine_type": EngineType.TORCH,
                    "Rec.lang_type": LangRec.CH,
                    "Rec.model_type": ModelType.SMALL,
                    "Rec.ocr_version": OCRVersion.PPOCRV6,
                    "Cls.do_clip": False,
                    # "EngineConfig.paddle.use_cuda": True,  # 使用PaddlePaddle GPU版推理
                    # "EngineConfig.paddle.cuda_ep_cfg.device_id": 0,  # 指定GPU id
                    "EngineConfig.torch.use_cuda": True,  # 使用 torch GPU 版推理
                    "EngineConfig.torch.cuda_ep_cfg.device_id": 0,  # 指定GPU id
                }
            )
            self._load_done = True
            print("✅ RapidOCR  初始化成功 (无警告)")

        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            sys.exit(1)

    @property
    def loaded(self) -> bool:
        return self._load_done

    class OCRResult(TypedDict):
        boxes: np.ndarray  # 坐标框数组，shape (N,4,2)
        txts: tuple[str, ...]  # 识别文本，和rapidocr原生一致（元组）
        scores: tuple[float, ...]  # 置信度，和rapidocr原生一致

    def _get_ocr_texts(self, res) -> OCRResult:

        # 优先取顶层（官方标准）
        if hasattr(res, "txts"):
            return {"boxes": res.boxes, "txts": res.txts, "scores": res.scores}
        # 异常结构兜底
        if hasattr(res, "det_output") and hasattr(res, "rec_output"):
            return {
                "boxes": res.det_output.boxes,
                "txts": res.rec_output.txts,
                "scores": res.rec_output.scores,
            }
        # 异常结构兜底
        return {
            "boxes": np.empty((0, 4, 2)),  # 空数组，保持 ndarray 类型
            "txts": (),
            "scores": (),
        }

    class XY_TYPE(TypedDict):
        left: int
        top: int
        width: int
        height: int

    @dataclass
    class Result_xy_type:
        x: int
        y: int

    SuccessRet = Tuple[Literal[True], Result_xy_type]
    FailRet = Tuple[Literal[False], None]

    def recognize_image(
        self, image_path: mss.ScreenShot, name: List[str], xy: XY_TYPE
    ) -> SuccessRet | FailRet:
        matched = []
        if not self._load_done or self.ocr is None:
            raise RuntimeError("OCR模型还未加载完成")
        try:
            img_np = np.array(image_path)
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
            # img_bgr = image_path
            result = self._get_ocr_texts(self.ocr(img_bgr))
            if not result or not result["txts"]:
                return False, None
            else:
                for idx, (box, text, score) in enumerate(
                    zip(result["boxes"], result["txts"], result["scores"])
                ):
                    if text:
                        # parsed_texts.append(text)
                        matched = [ch for ch in name if ch in text]

                        if matched:
                            x_min = int(box[:, 0].min())
                            y_min = int(box[:, 1].min())
                            x_max = int(box[:, 0].max())
                            y_max = int(box[:, 1].max())
                            data = self.Result_xy_type(
                                x=xy["left"] + x_min + (x_max - x_min) // 2,
                                y=xy["top"] + y_min + (y_max - y_min) // 2,
                            )

                            return True, data

                return False, None  # 👈 确保始终返回有效值
        except Exception as e:
            print(f"❌ 识别过程出错: {e}")
            # raise RuntimeError("OCR 识别过程出错") from e
            return False, None

    def is_number(self, val) -> bool:
        """判断是否为数字，包含正负整数、正负小数"""
        if isinstance(val, (int, float)):
            return True
        # 处理字符串形式数字
        if isinstance(val, str):
            val = val.strip()
            if not val:
                return False
            try:
                float(val)
                return True
            except ValueError:
                return False
        return False

    @dataclass
    class Coords_xy:
        x: Optional[int]
        y: Optional[int]

    def recognize_content(self, image_path: mss.ScreenShot) -> Coords_xy | None:

        try:
            if not self._load_done or self.ocr is None:
                raise RuntimeError("OCR模型还未加载完成")
            img_np = np.array(image_path)
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)

            result = self._get_ocr_texts(self.ocr(img_bgr))
            if not result or not result["txts"]:
                return None
            else:
                parsed_texts = []
                iter_data = list(zip(result["boxes"], result["txts"], result["scores"]))
                total = len(iter_data)
                for idx, (box, text, score) in enumerate(iter_data):
                    clean = text.replace("(", "").replace(")", "").strip()
                    if total <= 1:
                        first, rest = clean.split(",", 1)
                        if self.is_number(first) and self.is_number(rest):
                            return self.Coords_xy(int(first), int(rest))
                    else:
                        clean = clean.replace(",", "").strip()
                        if self.is_number(clean):
                            parsed_texts.append(int(clean))
                if len(parsed_texts) == 2:
                    return self.Coords_xy(parsed_texts[0], parsed_texts[1])
                else:
                    return None
        except Exception as e:
            print(f"❌ 识别过程出错: {e}")
            return None


ocr = Fish_ocr()


# 后台线程加载模型，不阻塞UI
def load_ocr_background():
    ocr._init_ocr()


# 启动加载线程（仅执行一次加载，加载完线程自动结束）
# load_thread = threading.Thread(target=load_ocr_background, daemon=True)
# load_thread.start()
