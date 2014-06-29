from database.base import Base
from sqlalchemy import Integer, String
from sqlalchemy import Column, ForeignKey

class MachineConfig(Base):
    __tablename__ = 'machines'

    id = Column(Integer, primary_key = True, autoincrement = True)
    vmx_path = Column(String, nullable = False)
    guest_user = Column(String, nullable = False)
    guest_password = Column(String, nullable = False)
    guest_base_path = Column(String, nullable = False)
    guest_shell_path = Column(String, nullable = False)
    guest_home_in_shell = Column(String, nullable = False)
    guest_build_script = Column(String, nullable = False)
    guest_run_script = Column(String, nullable = False)

    discriminator = Column('type', String, nullable = False, default = 'vmware')
    __mapper_args__ = { 'polymorphic_on' : discriminator }

class VMWareMachineConfig(MachineConfig):
    __tablename__ = 'vmwaremachines'
    __mapper_args__ = { 'polymorphic_identity' : 'vmware' }

    id = Column(Integer, primary_key = True, ForeignKey('machines.id'))
