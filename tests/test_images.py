from pathlib import Path
import importlib.util
import json
import tempfile
import unittest
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/'plugins/spec-extractor/skills/spec-extractor/scripts'
def load(name):
    spec=importlib.util.spec_from_file_location(name,SCRIPTS/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
images=load('image_tools');specs=load('spec_tools')

class ImageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def image(self,size=(123,321),name='source.png'):
        p=self.root/name
        with Image.new('RGB',size,'white') as im:im.save(p)
        return p
    def test_exact_received_pixels(self):
        p=self.image();m=images.inspect(p)
        self.assertEqual((m['width_px'],m['height_px']),(123,321))
        self.assertEqual(m['file'],'source.png');self.assertFalse(m['original_file_verified'])
        self.assertEqual(len(m['sha256']),64)
    def test_exif_orientation_and_cropped_pixels(self):
        p=self.root/'turned.jpg'
        with Image.new('RGB',(80,40),'red') as im:
            exif=Image.Exif();exif[274]=6;exif[270]='private description';im.save(p,exif=exif)
        m=images.inspect(p)
        self.assertEqual((m['stored_width_px'],m['stored_height_px']),(80,40))
        self.assertEqual((m['width_px'],m['height_px']),(40,80))
        out=self.root/'regions';images.regions(p,out,bbox=[0,40,40,80])
        with Image.open(out/'region-0001.png') as crop:
            self.assertEqual(crop.size,(40,40));self.assertFalse(crop.getexif())
    def test_bottom_right_fully_covered(self):
        areas=images.boxes(221,517,128,24)
        self.assertTrue(any(r==221 and b==517 for l,t,r,b in areas))
        for y in range(517):
            for x in range(221):self.assertTrue(any(l<=x<r and t<=y<b for l,t,r,b in areas))
    def test_invalid_box_does_not_create_output(self):
        p=self.image();out=self.root/'bad'
        with self.assertRaises(ValueError):images.regions(p,out,bbox=[0,0,124,321])
        self.assertFalse(out.exists())
    def test_existing_output_preserved(self):
        p=self.image();out=self.root/'existing';out.mkdir();(out/'keep').write_text('keep')
        with self.assertRaises(FileExistsError):images.regions(p,out)
        self.assertEqual((out/'keep').read_text(),'keep')
    def test_corrupt_file_rejected(self):
        p=self.image();p.write_bytes(p.read_bytes()[:45])
        with self.assertRaises((OSError,ValueError)):images.inspect(p)
    def test_multiframe_rejected(self):
        p=self.root/'multi.gif'
        with Image.new('RGB',(10,10),'red') as a,Image.new('RGB',(10,10),'blue') as b:
            a.save(p,save_all=True,append_images=[b])
        with self.assertRaises(ValueError):images.inspect(p)
    def test_tile_limits(self):
        for size,overlap in [(0,0),(128,128),(128,-1)]:
            with self.assertRaises(ValueError):images.boxes(200,200,size,overlap)
    def test_review_not_claimed(self):
        report=images.regions(self.image(),self.root/'tiles',size=128,overlap=24)
        self.assertEqual(report['coverage'],'full_image')
        self.assertTrue(all(r['review_status']=='not_reviewed' for r in report['regions']))

class EvidenceAndViewerTests(unittest.TestCase):
    def data(self):
        return json.loads((SCRIPTS.parent/'examples/sample-extraction.json').read_text())
    def test_bbox_bounds_checked(self):
        d=self.data();source=d['sources'][0];source.update(width_px=100,height_px=200,coordinate_space='exif_transposed_pixels')
        e=d['products'][0]['fields'][0]['evidence'][0]
        e.update(bbox_px=[0,0,100,200],coordinate_space='exif_transposed_pixels')
        self.assertEqual(specs.validate(d),[])
        e['bbox_px'][3]=201;self.assertTrue(any('bbox outside' in x for x in specs.validate(d)))
    def test_viewer_escapes_script_breakout(self):
        d=self.data();d['sources'][0]['file']='</script><script>alert(1)</script>'
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)/'export';specs.export(d,out)
            html=(out/'viewer.html').read_text()
            self.assertNotIn('</script><script>alert(1)',html)
            self.assertIn('\\u003c/script',html)
            self.assertNotIn('__SPEC_DATA__',html)
            self.assertEqual(json.loads((out/'specifications.json').read_text()),d)

if __name__=='__main__':unittest.main()
