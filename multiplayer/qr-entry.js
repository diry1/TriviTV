import QRCode from 'qrcode';
export const drawQR=(canvas,url)=>QRCode.toCanvas(canvas,url,{width:256,margin:2,color:{dark:'#101323',light:'#ffffff'}});
