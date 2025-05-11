import os
import json
from typing import Dict, List, Optional, Any, Tuple, cast, Union

import gradio

from facefusion import state_manager, wording
from facefusion.filesystem import resolve_relative_path
from facefusion.uis.core import register_ui_component
from facefusion.types import StateKey

PRESET_MANAGER_DROPDOWN : Optional[gradio.Dropdown] = None
PRESET_MANAGER_SAVE_BUTTON : Optional[gradio.Button] = None
PRESET_MANAGER_DELETE_BUTTON : Optional[gradio.Button] = None
PRESET_MANAGER_NAME_TEXTBOX : Optional[gradio.Textbox] = None

PRESETS_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'presets')


def render() -> None:
	global PRESET_MANAGER_DROPDOWN
	global PRESET_MANAGER_SAVE_BUTTON
	global PRESET_MANAGER_DELETE_BUTTON
	global PRESET_MANAGER_NAME_TEXTBOX

	preset_names = get_preset_names()
	
	with gradio.Group():
		with gradio.Row():
			PRESET_MANAGER_DROPDOWN = gradio.Dropdown(
				label = wording.get('uis.preset_manager_dropdown'),
				choices = preset_names,
				value = None,
				interactive = True
			)
			PRESET_MANAGER_NAME_TEXTBOX = gradio.Textbox(
				label = wording.get('uis.preset_manager_name_textbox'),
				placeholder = 'Enter preset name',
				interactive = True
			)
		with gradio.Row():
			PRESET_MANAGER_SAVE_BUTTON = gradio.Button(
				value = wording.get('uis.preset_manager_save_button'),
				variant = 'primary',
				size = 'sm'
			)
			PRESET_MANAGER_DELETE_BUTTON = gradio.Button(
				value = wording.get('uis.preset_manager_delete_button'),
				variant = 'stop',
				size = 'sm'
			)
	
	register_ui_component('preset_manager', PRESET_MANAGER_DROPDOWN)


def listen() -> None:
	if PRESET_MANAGER_DROPDOWN:
		PRESET_MANAGER_DROPDOWN.change(load_preset, inputs = PRESET_MANAGER_DROPDOWN)
	if PRESET_MANAGER_SAVE_BUTTON and PRESET_MANAGER_NAME_TEXTBOX and PRESET_MANAGER_DROPDOWN:
		PRESET_MANAGER_SAVE_BUTTON.click(save_preset, inputs = [PRESET_MANAGER_NAME_TEXTBOX, PRESET_MANAGER_DROPDOWN], outputs = [PRESET_MANAGER_NAME_TEXTBOX, PRESET_MANAGER_DROPDOWN])
	if PRESET_MANAGER_DELETE_BUTTON and PRESET_MANAGER_DROPDOWN:
		PRESET_MANAGER_DELETE_BUTTON.click(delete_preset, inputs = PRESET_MANAGER_DROPDOWN, outputs = PRESET_MANAGER_DROPDOWN)


def get_preset_names() -> List[Tuple[str, str]]:
	if not os.path.exists(PRESETS_DIRECTORY):
		os.makedirs(PRESETS_DIRECTORY, exist_ok=True)
	
	preset_files = [f for f in os.listdir(PRESETS_DIRECTORY) if f.endswith('.json')]
	preset_names = [(os.path.splitext(f)[0], os.path.splitext(f)[0]) for f in preset_files]
	
	return preset_names


def get_current_settings() -> Dict[str, Any]:
	settings = {}
	
	settings['temp_path'] = state_manager.get_item('temp_path')
	settings['jobs_path'] = state_manager.get_item('jobs_path')
	settings['source_paths'] = state_manager.get_item('source_paths')
	settings['target_path'] = state_manager.get_item('target_path')
	settings['output_path'] = state_manager.get_item('output_path')
	
	settings['face_detector_model'] = state_manager.get_item('face_detector_model')
	settings['face_detector_size'] = state_manager.get_item('face_detector_size')
	settings['face_detector_score'] = state_manager.get_item('face_detector_score')
	
	settings['face_selector_mode'] = state_manager.get_item('face_selector_mode')
	settings['face_selector_order'] = state_manager.get_item('face_selector_order')
	settings['reference_face_position'] = state_manager.get_item('reference_face_position')
	settings['reference_face_distance'] = state_manager.get_item('reference_face_distance')
	settings['reference_frame_number'] = state_manager.get_item('reference_frame_number')
	
	settings['face_mask_types'] = state_manager.get_item('face_mask_types')
	settings['face_mask_blur'] = state_manager.get_item('face_mask_blur')
	settings['face_mask_padding'] = state_manager.get_item('face_mask_padding')
	
	settings['trim_frame_start'] = state_manager.get_item('trim_frame_start')
	settings['trim_frame_end'] = state_manager.get_item('trim_frame_end')
	settings['temp_frame_format'] = state_manager.get_item('temp_frame_format')
	settings['keep_temp'] = state_manager.get_item('keep_temp')
	
	settings['output_image_quality'] = state_manager.get_item('output_image_quality')
	settings['output_image_resolution'] = state_manager.get_item('output_image_resolution')
	settings['output_video_encoder'] = state_manager.get_item('output_video_encoder')
	settings['output_video_preset'] = state_manager.get_item('output_video_preset')
	settings['output_video_quality'] = state_manager.get_item('output_video_quality')
	settings['output_video_resolution'] = state_manager.get_item('output_video_resolution')
	settings['output_video_fps'] = state_manager.get_item('output_video_fps')
	
	settings['processors'] = state_manager.get_item('processors')
	
	settings['execution_providers'] = state_manager.get_item('execution_providers')
	settings['execution_thread_count'] = state_manager.get_item('execution_thread_count')
	settings['execution_queue_count'] = state_manager.get_item('execution_queue_count')
	
	return settings


def apply_settings(settings: Dict[str, Any]) -> None:
	state = state_manager.get_state()
	for key, value in settings.items():
		if value is not None and key in state:
			try:
				state_manager.set_item(cast(StateKey, key), value)
			except (ValueError, TypeError):
				pass


def save_preset(preset_name: str, selected_preset: Optional[Any]) -> Tuple[str, gradio.Dropdown]:
	if not preset_name and not selected_preset:
		return "", gradio.Dropdown(choices=get_preset_names(), value=None)
	
	preset_name_str = preset_name
	
	if not preset_name_str:
		return "", gradio.Dropdown(choices=get_preset_names(), value=None)
	
	settings = get_current_settings()
	
	preset_path = os.path.join(PRESETS_DIRECTORY, f"{preset_name_str}.json")
	
	with open(preset_path, 'w', encoding='utf-8') as f:
		json.dump(settings, f, indent=4, ensure_ascii=False)
	
	preset_names = get_preset_names()
	selected_value = None
	
	for choice in preset_names:
		if choice[0] == preset_name_str:
			selected_value = choice
			break
	
	return "", gradio.Dropdown(choices=preset_names, value=selected_value)


def load_preset(preset_name: Optional[Any]) -> None:
	if not preset_name:
		return
	
	if isinstance(preset_name, (tuple, list)) and len(preset_name) > 0:
		preset_name_str = preset_name[0]
	else:
		preset_name_str = preset_name
	
	preset_path = os.path.join(PRESETS_DIRECTORY, f"{preset_name_str}.json")
	
	if not os.path.exists(preset_path):
		return
	
	with open(preset_path, 'r', encoding='utf-8') as f:
		settings = json.load(f)
	
	apply_settings(settings)


def delete_preset(preset_name: Optional[Any]) -> gradio.Dropdown:
	if not preset_name:
		return gradio.Dropdown(choices=get_preset_names(), value=None)
	
	if isinstance(preset_name, (tuple, list)) and len(preset_name) > 0:
		preset_name_str = preset_name[0]
	else:
		preset_name_str = preset_name
	
	preset_path = os.path.join(PRESETS_DIRECTORY, f"{preset_name_str}.json")
	
	if os.path.exists(preset_path):
		os.remove(preset_path)
	
	preset_names = get_preset_names()
	return gradio.Dropdown(choices=preset_names, value=None)
