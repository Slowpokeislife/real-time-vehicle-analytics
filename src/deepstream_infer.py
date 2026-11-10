"""Legacy NVIDIA DLI/DeepStream Python GStreamer pipeline for one H264 stream.

Requires Linux + NVIDIA DeepStream, gst-python and matching pyds.
The original course used this GStreamer API; latest DeepStream may require
porting to PyServiceMaker. Not tested on the current host.
"""
import argparse
from pathlib import Path
from src.tailgating import Box,frame_flag

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',required=True,help='Annex-B H264 input (e.g. demo/assessment_stream.h264)')
    parser.add_argument('--config',default='configs/dashcamnet.txt')
    parser.add_argument('--output',default='outputs/annotated.mpeg4')
    parser.add_argument('--log',default='outputs/tailgating_flags.txt')
    parser.add_argument('--width',type=int,default=1280)
    parser.add_argument('--height',type=int,default=720)
    args=parser.parse_args()
    if not Path(args.input).is_file():parser.error('Input video not found')
    if not Path(args.config).is_file():parser.error('Inference config not found')
    for f in [args.output,args.log]:Path(f).parent.mkdir(parents=True,exist_ok=True)
    try:
        import gi
        gi.require_version('Gst','1.0')
        from gi.repository import Gst,GLib
        import pyds
    except (ImportError,ValueError) as exc:
        parser.error('This pipeline requires Linux, DeepStream, Gst Python and pyds: '+str(exc))
    Gst.init(None)
    pipeline=Gst.Pipeline.new('tailgating-detection')
    def make(plugin,name):
        element=Gst.ElementFactory.make(plugin,name)
        if element is None:raise RuntimeError(f'GStreamer plugin not found: {plugin}')
        pipeline.add(element);return element
    source=make('filesrc','source');source.set_property('location',str(Path(args.input).resolve()))
    parser_h264=make('h264parse','h264-parser')
    decoder=make('nvv4l2decoder','decoder')
    mux=make('nvstreammux','streammux');mux.set_property('width',args.width);mux.set_property('height',args.height)
    mux.set_property('batch-size',1);mux.set_property('batched-push-timeout',4000000)
    mux.set_property('live-source',0)
    inference=make('nvinfer','primary-inference');inference.set_property('config-file-path',str(Path(args.config).resolve()))
    convert1=make('nvvideoconvert','convert1')
    osd=make('nvdsosd','osd')
    convert2=make('nvvideoconvert','convert2')
    capsfilter=make('capsfilter','cpu-i420')
    capsfilter.set_property('caps',Gst.Caps.from_string('video/x-raw,format=I420'))
    encoder=make('avenc_mpeg4','encoder');encoder.set_property('bitrate',2000000)
    sink=make('filesink','sink');sink.set_property('location',str(Path(args.output).resolve()))
    sink.set_property('sync',False)
    def link(a,b):
        if not a.link(b):raise RuntimeError(f'Could not link {a.name} to {b.name}')
    link(source,parser_h264);link(parser_h264,decoder)
    decoder_pad=decoder.get_static_pad('src');mux_pad=mux.request_pad_simple('sink_0') if hasattr(mux,'request_pad_simple') else mux.get_request_pad('sink_0')
    if not mux_pad or decoder_pad.link(mux_pad)!=Gst.PadLinkReturn.OK:raise RuntimeError('Failed to link decoder to mux')
    chain=[mux,inference,convert1,osd,convert2,capsfilter,encoder,sink]
    for a,b in zip(chain,chain[1:]):link(a,b)
    flags=[]
    def probe(pad,info,user_data):
        buffer=info.get_buffer()
        if buffer is None:return Gst.PadProbeReturn.OK
        batch=pyds.gst_buffer_get_nvds_batch_meta(hash(buffer))
        if batch is None:return Gst.PadProbeReturn.OK
        frames=batch.frame_meta_list
        while frames is not None:
            frame=pyds.NvDsFrameMeta.cast(frames.data)
            boxes=[]; objs=frame.obj_meta_list
            while objs is not None:
                obj=pyds.NvDsObjectMeta.cast(objs.data)
                rect=obj.rect_params
                label=str(obj.obj_label or '').strip()
                boxes.append(Box(float(rect.left),float(rect.top),float(rect.width),float(rect.height),label))
                try: objs=objs.next
                except StopIteration:break
            flags.append(frame_flag(boxes,args.width,args.height))
            try:frames=frames.next
            except StopIteration:break
        return Gst.PadProbeReturn.OK
    pad=osd.get_static_pad('sink');pad.add_probe(Gst.PadProbeType.BUFFER,probe,None)
    loop=GLib.MainLoop();bus=pipeline.get_bus();bus.add_signal_watch()
    errors=[]
    def on_bus(bus,msg):
        if msg.type==Gst.MessageType.ERROR:
            err,debug=msg.parse_error();errors.append(f'{err}: {debug}');loop.quit()
        elif msg.type==Gst.MessageType.EOS:loop.quit()
    bus.connect('message',on_bus)
    try:
        status=pipeline.set_state(Gst.State.PLAYING)
        if status==Gst.StateChangeReturn.FAILURE:raise RuntimeError('Pipeline could not enter PLAYING state')
        loop.run()
    finally:
        pipeline.set_state(Gst.State.NULL)
        Path(args.log).write_text('\n'.join(map(str,flags))+('\n' if flags else ''),encoding='utf8')
    if errors:raise RuntimeError('Pipeline failure: '+'; '.join(errors))
    print(f'Frames logged: {len(flags)}. Flagged frames: {sum(flags)}. Output: {args.output}. Log: {args.log}')
if __name__=='__main__':main()
