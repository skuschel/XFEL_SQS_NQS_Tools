from sqs_nqs_tools.offline import access, data

p = "/gpfs/exfel/exp/SQS/201802/p002195/scratch"

[t_id,tof,pix] = data.getTOF( 100, path=p)

print(t_id.shape)
print(tof.shape)
