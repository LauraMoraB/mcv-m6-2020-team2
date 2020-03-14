from src.utils.track import Track
from src.evaluation.intersection_over_union import bb_intersecion_over_union

def update_tracks(tracks, new_detections, max_track, method):
    if method == 'overlap':
        return update_tracks_by_overlap(tracks, new_detections, max_track)
    elif method == 'kalman':
        return update_tracks_by_overlap(tracks, new_detections, max_track)

def update_tracks_by_overlap(tracks, new_detections, max_track):
    frame_tracks = []
    for track in tracks:
        # Compare track detection in last frame with new detections
        matched_detection = match_next_bbox(track.last_detection(), new_detections)
        # If there's a match, refine detections
        if matched_detection:
            refined_detection = refine_bbox(track.last_detection(), matched_detection)
            track.add_detection(refined_detection)
            frame_tracks.append(track)
            new_detections.remove(matched_detection)

    # Update tracks with unused detections after matching
    for unused_detection in new_detections:
        unused_detection.id = max_track + 1
        new_track = Track(max_track + 1, [unused_detection])
        tracks.append(new_track)
        frame_tracks.append(new_track)
        max_track += 1

    return tracks, frame_tracks, max_track

def update_tracks_by_kalman(tracks, new_detections, max_track):
    #TODO
    return tracks, new_detections, max_track

def refine_bbox(last_detection, new_detection):
    # TODO Refinement
    return new_detection

def match_next_bbox(last_detection, unused_detections):
    max_iou = 0
    for detection in unused_detections:
        iou = bb_intersecion_over_union(last_detection.bbox, detection.bbox)
        if iou > max_iou:
            max_iou = iou
            best_match = detection
    if max_iou > 0:
        best_match.id = last_detection.id
        return best_match
    else:
        return None